import argparse
from typing import Dict, Any, List, Optional, Callable

class Extend(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # Get current list (or initialize with empty list if None)
        items = getattr(namespace, self.dest, []) or []
        
        # Only extend if values is not None (protect against edge cases)
        if values is not None:
            items.extend(values)
        
        # Update the namespace
        setattr(namespace, self.dest, items)
        
class CustomHelpFormatter(argparse.RawTextHelpFormatter):
    def _format_help(self):
        return generate_readme_console()
    
    
class ArgParser():
    
    def __init__(self):
        pass
    
    def _get_args(self):
        pass
    
    def format_default(self,value):
        """Format default values for display"""
        if value is None:
            return "None"
        if isinstance(value, bool):
            return str(value)
        if isinstance(value, str):
            return f'"{value}"' if value else '""'
        if isinstance(value, list):
            return "[]" if not value else str(value)
        return str(value)
    
    def add_args(self,parser,args):
        """Add arguments without any special handling"""
        args_config = args
        
        for arg_name, config in args.items():
            kwargs = {
                'help': config['help'],
                'default': config.get('default'), 
            }
            
            # Add optional parameters
            for param in ['action', 'nargs', 'choices', 'type']:
                if param in config:
                    kwargs[param] = config[param]
            
            # Handle option strings
            option_strings = [config['short'], config['long']]
            if 'alt_long' in config:
                option_strings.append(config['alt_long'])
            
            parser.add_argument(*option_strings, **kwargs)
            
    def add_parsers(self, subparsers, parsers_kwargs):
        """Add multiple subparsers from a dictionary of kwargs and return them.
        
        Args:
            subparsers: The subparsers object from argparse.
            parsers_kwargs: Dict of {parser_name: kwargs} for each subparser.
            
        Returns:
            Dict[str, ArgumentParser]: A dictionary of created subparsers.
        """
        created_parsers = {}
        for parser_name, kwargs in parsers_kwargs.items():
            created_parsers[parser_name] = subparsers.add_parser(parser_name, **kwargs)
            
        return created_parsers
            
    def validate_args(self):
        """Ensure all configured args exist in the parser"""
        import argparse
        parser = argparse.ArgumentParser()
        add_shared_args(parser)
        
        configured_args = {v['long'] for v in get_shared_args_config().values()}
        parser_args = {a.option_strings[-1] for a in parser._actions 
                    if a.option_strings and not a.option_strings[0].startswith('-h')}
        
        missing = configured_args - parser_args
        if missing:
            raise RuntimeError(f"Args in config but not in parser: {missing}")
    
    def get_display_value(arg_info, field):
        """Helper to get field from _display first, then main dict"""
        if '_display' in arg_info and field in arg_info['_display']:
            return arg_info['_display'][field]
        return arg_info.get(field)  # Fallback to main dict

    def process_arg_for_table(args_dict):
        rows = []
        
        for arg_name, arg_info in args_dict.items():
            rows.append([
                # Option (always combined from main dict)
                f"{arg_info['short']}/{arg_info['long']}",
                
                # Description (_display help -> main help)
                get_display_value(arg_info, 'help'),
                
                # Type (_display type -> auto-detect)
                get_display_value(arg_info, 'type') or (
                    "Flag" if arg_info.get('action') else
                    "File" if arg_info.get('type') == str else
                    "Text"
                ),
                
                # Default (_display default -> main default)
                str(get_display_value(arg_info, 'default') or ""),
                
                # Category (_display category -> default "General")
                get_display_value(arg_info, 'category') or "General"
            ])
    
            return rows
