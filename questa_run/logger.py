import logging
import sys
import os
from datetime import datetime
from typing import Optional, Union, Dict, Any, List, Tuple
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import traceback
import json
from functools import wraps
import time

class Logger:
    """
    A comprehensive logging utility without color formatting.
    
    Features:
    - Multiple log rotation strategies (size/time-based)
    - JSON logging support
    - System metrics logging (CPU, memory)
    - Log compression for archived files
    - Thread-safe and process-safe operations
    - Separated initialization and logging start
    """

    _DEFAULT_FORMATS = {
        'multithread': (
            '# %(asctime)s [%(levelname)-8s] [%(process)d:%(threadName)s] '
            '%(module)s:%(lineno)d %(message)s'
        ),
        'default': (
            '# %(asctime)s [%(levelname)-8s] '
            '%(module)s:%(lineno)d %(message)s'
        )
    }

    def __init__(self, 
                log_file: str, 
                name: str = "Logger",
                level: Union[int, str] = logging.INFO,
                console: bool = True,
                start_msg: Optional[str] = None,
                end_msg: Optional[str] = None,
                max_files: int = 100,
                max_bytes: int = 1024 * 1024 * 1024,  # 1GB
                when: Optional[str] = None,  # 'midnight', 'H', 'D', etc.
                backup_count: int = 30,
                format_str: Optional[str] = None,
                date_format: str = "%H:%M:%S",
                json: bool = False,
                multithread: bool = False,
                simple: bool = True,
                email_config: Optional[Dict[str, Any]] = None,
                buffer_logs: bool = True):
        """
        Initialize the logger without starting logging immediately.
        """
        self.log_file = log_file
        self.name = name
        self.json = json
        self.multithread = multithread
        self.simple = simple
        self._console_enabled = console  # Track console state
        self._max_files = max_files
        self._max_bytes = max_bytes
        self._when = when
        self._backup_count = backup_count
        self._buffer_logs = buffer_logs
        self._log_buffer = []
        self._logging_started = False
        
        # Convert string level to numeric
        self._level = self._parse_log_level(level)
        
        # Initialize counters
        self.counts = {
            'DEBUG': 0,
            'INFO': 0,
            'WARNING': 0,
            'ERROR': 0,
            'CRITICAL': 0
        }
        
        # Set default messages
        self.start_msg = start_msg or self._default_start_message()
        self.end_msg = end_msg or self._default_end_message()
        
        # Initialize but don't configure handlers yet
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(self._level)
        self._logger.propagate = False
        
        # Choose appropriate format
        format_key = 'multithread' if self.multithread else 'default'
        default_format = self._DEFAULT_FORMATS[format_key]
        
        self._formatter = logging.Formatter(
            format_str or default_format,
            datefmt=date_format
        )
        
        if self.json:
            self._json_formatter = logging.Formatter('%(message)s')

        # Will be set when logging starts
        self.start_time = None
        self._metrics_enabled = False
        self._last_metrics_log = None

    def start_logging(self, log_file: Optional[str] = None):
        """
        Start the logging process after all configurations are set.
        
        Args:
            log_file: Optional new log file path. If provided, will override the initial log file path.
        """
        if log_file is not None:
            self.log_file = log_file
            
        self.start_time = datetime.now()
        self._configure_handlers(
            console=self._console_enabled,
            max_files=self._max_files,
            max_bytes=self._max_bytes,
            when=self._when,
            backup_count=self._backup_count
        )
        
        # Format the start message with actual timestamp and date
        formatted_start_msg = self.start_msg.format(
            timestamp=self.start_time.strftime('%H:%M:%S'),
            date=self.start_time.strftime('%Y-%m-%d')
        )
        
        self._logging_started = True
        

        
        self.process_info("\n"+formatted_start_msg)
        self.info(f"Logger '{self.name}' initialized")
        self._log_system_info()
        
        # Flush any buffered logs
        self._flush_buffer()

    def _parse_log_level(self, level: Union[int, str]) -> int:
        """Convert string level to numeric level."""
        if isinstance(level, str):
            return getattr(logging, level.upper(), logging.INFO)
        return level

    def _default_start_message(self) -> str:
        """Generate default start message."""
        return (
            f"# === Process Start Time: {'{timestamp}'} "
            f"on {'{date}'} ==="
        )

    def _default_end_message(self) -> str:
        """Generate default end message."""
        return (
            "# === PROCESS COMPLETED: {end_time} ===\n"
            "# === DURATION: {duration:.2f} seconds ===\n"
            "# === COUNTS: DEBUG={debug}, INFO={info}, WARNING={warn}, "
            "# ERROR={error}, CRITICAL={critical} ==="
        )

    def _configure_handlers(self, console: bool, max_files: int, max_bytes: int,
                          when: Optional[str], backup_count: int):
        """Configure file and console handlers."""
        # Ensure directory exists
        log_dir = os.path.dirname(self.log_file) or '.'
        os.makedirs(log_dir, exist_ok=True)
        
        # Create appropriate file handler
        file_handler = self._create_file_handler(
            max_files=max_files,
            max_bytes=max_bytes,
            when=when,
            backup_count=backup_count
        )
        
        file_handler.setFormatter(self._formatter)
        self._logger.addHandler(file_handler)
        
        if console:
            # Check if a StreamHandler already exists
            for handler in self._logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    break  # Skip adding another one
            else:
                self._add_console_handler()

    def _create_file_handler(self, max_files: int, max_bytes: int,
                           when: Optional[str], backup_count: int) -> logging.Handler:
        """Create appropriate file handler based on rotation strategy."""
        if when:
            return TimedRotatingFileHandler(
                self.log_file,
                when=when,
                backupCount=backup_count,
                encoding='utf-8'
            )
        return RotatingFileHandler(
            self.log_file,
            maxBytes=max_bytes,
            backupCount=max_files,
            encoding='utf-8',
            delay=True  # Helps with multi-process safety
        )

    def _add_console_handler(self):
        """Add a console handler to the logger."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self._formatter)
        self._logger.addHandler(console_handler)
        self._console_enabled = True
        
    @property
    def console_enabled(self) -> bool:
        """Check if console logging is currently enabled."""
        return self._console_enabled

    def enable_console(self):
        """Enable console logging if not already enabled."""
        if not self._console_enabled:
            self._add_console_handler()
            self._console_enabled = True


    def disable_console(self):
        """Disable console logging if currently enabled."""
        if self._console_enabled:
            for handler in self._logger.handlers[:]:
                if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                    self._logger.removeHandler(handler)
                    handler.close()
            self._console_enabled = False


    def toggle_console(self, state: Optional[bool] = None):
        """
        Toggle console logging on/off.
        
        Args:
            state: If None, toggles current state. If True/False, sets to that state.
        """
        if state is None:
            state = not self._console_enabled
        
        if state:
            self.enable_console()
        else:
            self.disable_console()

    def _configure_email_alerts(self, email_config: Dict[str, Any]):
        """Configure email alerts for critical errors."""
        from logging.handlers import SMTPHandler
        
        mail_handler = SMTPHandler(
            mailhost=(email_config['host'], email_config.get('port', 25)),
            fromaddr=email_config['from_addr'],
            toaddrs=email_config['to_addrs'],
            subject=email_config.get('subject', f'Critical Error in {self.name}'),
            credentials=(email_config['username'], email_config['password']),
            secure=() if email_config.get('tls') else None
        )
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(logging.Formatter("""
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
"""))
        self._logger.addHandler(mail_handler)

    def _log_system_info(self):
        """Log basic system information."""
        try:
            import platform
            self.info(f"System: {platform.system()} {platform.release()}")
            self.info(f"Python: {platform.python_version()}")
            self.info(f"Process ID: {os.getpid()}")
        except Exception as e:
            self.warning(f"Could not log system info: {str(e)}")

    def enable_metrics(self):
        """Enable system metrics to be logged only at shutdown"""
        try:
            import psutil
            self._metrics_enabled = True
        except ImportError:
            self.warning("psutil not installed, metrics disabled")

    def _log_metrics(self):
        """Log system metrics (only called at shutdown)."""
        if not self._metrics_enabled:
            return
            
        try:
            import psutil
            
            # Prevent recursive logging
            if hasattr(self, '_logging_metrics'):
                return
                
            self._logging_metrics = True
            
            metrics = self._collect_system_metrics()
            
            if self.json:
                self._log_json_metrics(metrics)
            else:
                self._log_text_metrics(metrics)
                
        except Exception as e:
            self._logger.warning(f"Failed to log metrics: {str(e)}")
        finally:
            if hasattr(self, '_logging_metrics'):
                del self._logging_metrics

    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics using psutil."""
        import psutil
        
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'type': 'metrics',
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu,
            'memory_total': mem.total,
            'memory_used': mem.used,
            'memory_percent': mem.percent,
            'disk_total': disk.total,
            'disk_used': disk.used,
            'disk_percent': disk.percent
        }

    def _log_json_metrics(self, metrics: Dict[str, Any]):
        """Log metrics in JSON format."""
        original_state = self._metrics_enabled
        self._metrics_enabled = False
        self.info(json.dumps(metrics))
        self._metrics_enabled = original_state

    def _log_text_metrics(self, metrics: Dict[str, Any]):
        """Log metrics in text format."""
        msg = (
            "\n# =============== FINAL SYSTEM METRICS ==============="
            f"\n# CPU Usage: {metrics['cpu_percent']}%"
            f"\n# Memory Usage: {metrics['memory_percent']}% "
            f"({metrics['memory_used']//(1024*1024)}MB of {metrics['memory_total']//(1024*1024)}MB)"
            f"\n# Disk Usage: {metrics['disk_percent']}% "
            f"({metrics['disk_used']//(1024*1024)}MB of {metrics['disk_total']//(1024*1024)}MB)"
            "\n# ===================================================="
        )
        self.log(logging.INFO, msg, simple=True)

    def add_context(self, **context):
        """Add contextual information to all subsequent logs."""
        if not hasattr(self, '_context'):
            self._context = {}
        self._context.update(context)
        
    def log(self, level: int, message: str, **kwargs):
        """Generic log method with additional context."""
        
        if not self._logging_started and self._buffer_logs:
            # Store the log in buffer if logging hasn't started yet
            self._log_buffer.append((level, message, kwargs))
            return
        
        if hasattr(self, '_context'):
            kwargs.update(self._context)
            
        level_name = logging.getLevelName(level)
        self.counts[level_name] += 1
        
        if self.json:
            self._log_json(level, level_name, message, kwargs)
        else:
            self._log_text(level, message, kwargs)
            
    def _flush_buffer(self):
        """Flush all buffered logs to the actual logger."""
        if not self._log_buffer:
            return
            
        # Log a message about flushing the buffer
        self.line()
        self.underline(f'Append Buffered Logs')
        self.info(f"Flushing {len(self._log_buffer)} buffered log messages")
        
        for level, message, kwargs in self._log_buffer:
            # Re-log the message now that logging is started
            if hasattr(self, '_context'):
                kwargs.update(self._context)
                
            level_name = logging.getLevelName(level)
            self.counts[level_name] += 1
            
            if self.json:
                self._log_json(level, level_name, message, kwargs)
            else:
                self._log_text(level, message, kwargs)
                
        self._log_buffer.clear()
        self.line()

    def _log_json(self, level: int, level_name: str, message: str, kwargs: Dict[str, Any]):
        """Handle JSON formatted logging."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level_name,
            'message': message,
            **kwargs
        }
        self._logger.log(level, json.dumps(log_entry))

    def _log_text(self, level: int, message: str, kwargs: Dict[str, Any]):
        """Handle text formatted logging."""
        if self.simple:
            self._log_simple_text(level, message)
        else:
            extra = {'custom_data': kwargs} if kwargs else None
            self._logger.log(level, message, extra=extra)

    def _log_simple_text(self, level: int, message: str):
        """Handle simple text logging with minimal formatting."""
        original_formatters = []
        for handler in self._logger.handlers:
            original_formatters.append(handler.formatter)
            handler.setFormatter(logging.Formatter('%(message)s'))
        
        self._logger.log(level, message)
        
        # Restore original formatters
        for handler, formatter in zip(self._logger.handlers, original_formatters):
            handler.setFormatter(formatter)
       
    def set_level(self, level: Union[int, str]):
        """Dynamically change the logging level."""
        self._level = self._parse_log_level(level)
        self._logger.setLevel(self._level)
        for handler in self._logger.handlers:
            handler.setLevel(self._level)
    
    # Shortcut methods (debug, info, warning, error, critical)
    def debug(self, message: str, **kwargs):
        self.log(logging.DEBUG, f"# ** {logging.getLevelName(logging.DEBUG)}: "+message, **kwargs)

    def info(self, message: str, **kwargs):
        self.log(logging.INFO, "# -- "+ message, **kwargs)
        
    def header(self, message: str, align_centre: bool = True, symbol: str = '-', debug: bool = False, newline: bool = True, **kwargs):
        char_count = len(message)
        left_padding = ' ' * ((100 - char_count) // 2)
        right_padding = ' ' * (100 - char_count - len(left_padding) + 2)
        if align_centre:
            self.line(symbol=symbol,newline=False,debug=debug)
            self.log(logging.INFO if not debug else logging.DEBUG, '#' + left_padding + f"{message}" + right_padding + '#', **kwargs)
            self.line(symbol=symbol,newline=newline,debug=debug)
        else:
            self.line(number=char_count,symbol=symbol,newline=False,debug=debug)
            self.log(logging.INFO if not debug else logging.DEBUG, f'# {message} #', **kwargs)
            self.line(number=char_count,symbol=symbol,newline=newline,debug=debug)
        
    def underline(self, message: str, **kwargs):
        # Count the number of characters (including spaces)
        char_count = len(message)
        # Create the underline with dashes
        underline = '-' * char_count
        self.log(logging.INFO, f"# {message}\n# {underline}", **kwargs)
    
    def note(self, message: str, **kwargs):
        self.log(logging.INFO, "# ** Note: "+ message, **kwargs)

    def process_info(self, message: str, debug: bool = False, **kwargs):
        self.log(logging.INFO if not debug else logging.DEBUG, "# "+message, **kwargs)
        
    def line(self, number: int = 100, symbol: str = '-', newline: bool = True, debug=False,**kwargs):
        if newline:
            self.log(logging.INFO if not debug else logging.DEBUG, '# ' + symbol * number + ' #' + '\n# ', **kwargs) 
        else:
            self.log(logging.INFO if not debug else logging.DEBUG, '# ' + symbol * number + ' #', **kwargs)
        
    def space(self, number: int = 1, debug: bool = False):
        self.log(logging.INFO if not debug else logging.DEBUG, '#')
        if number > 1:
            self.space(number-1)

    def warning(self, message: str, **kwargs):
        self.log(logging.WARNING, f"# ** {logging.getLevelName(logging.WARNING)}: "+message, **kwargs)

    def error(self, message: str, **kwargs):
        self.log(logging.ERROR, f"# ** {logging.getLevelName(logging.ERROR)}: "+message, **kwargs)

    def critical(self, message: str, **kwargs):
        self.log(logging.CRITICAL, f"# ** {logging.getLevelName(logging.CRITICAL)}: "+message, **kwargs)

    def exception(self, message: str, exc_info: bool = True, **kwargs):
        """Log an exception with stack trace."""
        self.counts['ERROR'] += 1
        exc_details = {
            'exception_type': str(type(exc_info[1])) if isinstance(exc_info, tuple) else None,
            'exception_message': str(exc_info[1]) if isinstance(exc_info, tuple) else None,
            'stack_trace': traceback.format_exc(),
            **kwargs
        }
        
        if self.json:
            self.error(message, **exc_details)
        else:
            self._logger.exception(message, exc_info=exc_info, extra={'custom_data': kwargs})

    def add_handler(self, handler: logging.Handler):
        """Add a custom logging handler."""
        handler.setFormatter(self._json_formatter if self.json else self._formatter)
        self._logger.addHandler(handler)

    def switch_log_file(self, new_log_file: str, keep_handlers: bool = False):
        """
        Switch logging to a new file while maintaining the same configuration.
        
        Args:
            new_log_file: Path to the new log file (e.g., "Results/questa_run.log")
            keep_handlers: If True, keeps existing handlers (including console)
        """
        # Close and remove existing file handlers
        for handler in self._logger.handlers[:]:
            if isinstance(handler, (RotatingFileHandler, TimedRotatingFileHandler)):
                if not keep_handlers:
                    handler.close()
                    self._logger.removeHandler(handler)
        
        # Update the log file path
        self.log_file = new_log_file
        
        # Ensure directory exists (handle both relative and absolute paths)
        log_dir = os.path.dirname(os.path.abspath(self.log_file))
        os.makedirs(log_dir, exist_ok=True)  # Creates dir if it doesn't exist
        
        # Recreate file handlers with existing rotation settings
        file_handler = self._create_file_handler(
            max_files=self._max_files,
            max_bytes=self._max_bytes,
            when=self._when,
            backup_count=self._backup_count
        )
        
        # Disable delay to force file creation
        file_handler.delay = False
        
        file_handler.setFormatter(self._formatter)
        self._logger.addHandler(file_handler)
        
        # Force file creation (if it doesn't exist)
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w'):
                pass  # Touch the file
            
        self.info(f"Log file switched to: {new_log_file}")

    def get_stats(self) -> Dict[str, Any]:
        """Get detailed logging statistics."""
        return {
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': datetime.now().isoformat(),
            'duration_seconds': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            'counts': self.counts,
            'total_logs': sum(self.counts.values()),
            'log_file': self.log_file,
            'log_file_size': os.path.getsize(self.log_file) if os.path.exists(self.log_file) else 0
        }

    def compress_logs(self, output_file: Optional[str] = None) -> Optional[str]:
        """Compress current log file."""
        import gzip
        output_file = output_file or f"{self.log_file}.gz"
        
        try:
            with open(self.log_file, 'rb') as f_in, gzip.open(output_file, 'wb') as f_out:
                f_out.writelines(f_in)
            return output_file
        except Exception as e:
            self.error(f"Failed to compress logs: {str(e)}")
            return None

    def generate_summary(self):
        """Generate a summary of warnings and errors."""
        if self.counts['WARNING'] > 0 or self.counts['ERROR'] > 0:
            self.process_info("\n# === EXECUTION SUMMARY ===")
            self.process_info(f"# Warnings: {self.counts['WARNING']}")
            self.process_info(f"# Errors: {self.counts['ERROR']}")
            if self.counts['CRITICAL'] > 0:
                self.process_info(f"# FATAL: {self.counts['CRITICAL']}")
                
    def __enter__(self):
        """Context manager entry point."""
        self.start_logging()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        if exc_type:
            self.exception("Exception occurred", exc_info=(exc_type, exc_val, exc_tb))
        
        self._log_final_stats()
        self._log_metrics()
        self.generate_summary()
        self.close()
        return False

    def _log_final_stats(self):
        """Log final statistics before shutdown."""
        if not self.start_time:
            return
            
        stats = self.get_stats()
        end_message = self.end_msg.format(
            end_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            duration=stats['duration_seconds'],
            debug=stats['counts']['DEBUG'],
            info=stats['counts']['INFO'],
            warn=stats['counts']['WARNING'],
            error=stats['counts']['ERROR'],
            critical=stats['counts']['CRITICAL']
        )
        self.process_info("\n" + end_message)

    def close(self):
        """Clean up resources."""
        
        # Flush any remaining logs before closing
        if not self._logging_started and self._buffer_logs:
            self._flush_buffer()
            
        for handler in self._logger.handlers[:]:
            handler.close()
            self._logger.removeHandler(handler)
            
    # Additional logging methods
    def log_config(self, config: Dict, name: str = "Configuration"):
        """Log a configuration dictionary in readable format."""
        self.info(f"\n=== {name} ===")
        for key, value in config.items():
            self.info(f"{key:>20}: {value}")
        self.info("=" * (len(name) + 6))
        
    def log_command(self, command: Union[str, List[str]], tool: str, **kwargs):
        """Log a command being executed with timing information."""
        if isinstance(command, list):
            command = ' '.join(command)
        self.info(f"Executing {tool} command: {command}", **kwargs)
    
    def log_results(self, results: Dict, success: bool = True):
        """Log final results of the execution."""
        status = "SUCCESS" if success else "FAILURE"
        self.info(f"\n=== FINAL RESULT: {status} ===")
        for metric, value in results.items():
            self.info(f"{metric:>20}: {value}")
        
    def capture_tool_output(self, process, log_level=logging.INFO):
        """Capture and log output from a subprocess."""
        for line in iter(process.stdout.readline, b''):
            self.log(log_level, line.decode().strip())
            
    def timed(self, message=None):
        """Decorator to log execution time of functions."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                msg = message or f"Function {func.__name__} executed"
                self.info(f"{msg} in {elapsed:.2f}s")
                return result
            return wrapper
        return decorator
    
    def phase_start(self, phase_name: str):
        """Mark the start of a new phase."""
        self.info(f"\n=== PHASE START: {phase_name.upper()} ===")
        self._current_phase = phase_name
        self._phase_start_time = time.time()

    def phase_end(self):
        """Mark the end of the current phase."""
        if hasattr(self, '_current_phase'):
            elapsed = time.time() - self._phase_start_time
            self.info(f"=== PHASE END: {self._current_phase.upper()} ({elapsed:.2f}s) ===\n")
            
    def verify_file(self, filepath: str, check_writeable: bool = False):
        """Verify file exists and optionally check write permissions."""
        if not os.path.exists(filepath):
            self.error(f"File not found: {filepath}")
            return False
        if check_writeable and not os.access(filepath, os.W_OK):
            self.error(f"File not writeable: {filepath}")
            return False
        return True
        
    def progress_start(self, total: int, description: str = ""):
        """Initialize a progress tracker."""
        self._progress_total = total
        self._progress_current = 0
        self._progress_description = description
        self.info(f"{description} [{' ' * 50}] 0%", simple=True)

    def progress_update(self, increment: int = 1):
        """Update progress."""
        self._progress_current += increment
        percent = min(100, (self._progress_current / self._progress_total) * 100)
        bars = '=' * int(percent // 2)
        self.info(f"{self._progress_description} [{bars:<50}] {percent:.1f}%", simple=True)
        
    def log_path(self, path: str, description: str = "Path"):
        """Log a path in platform-appropriate format."""
        normalized = os.path.normpath(path)
        self.info(f"{description}: {normalized}")

if __name__ == "__main__":
    # Example usage
    logger = Logger(
        "app.log",
        name="ExampleLogger",
        level="DEBUG",
        max_files=5,
        max_bytes=10*1024*1024,  # 10MB
        json=False,
        simple=True
    )
    
    # You can modify settings here before starting logging
    logger.set_level("INFO")
    logger.disable_console()
    
    # Now start logging
    logger.start_logging()
    
    logger.enable_metrics()
    logger.info("Application started")
    logger.note("This is a Note.")
    logger.debug("Debugging information")
    logger.warning("This is a warning")
    logger.error("This is an error")
    logger.info("Compiling File")
    try:
        1 / 0
    except Exception as e:
        logger.exception("Math error occurred")
    
    logger.critical("Critical issue", extra_data={"user": "test"})
    logger.close()