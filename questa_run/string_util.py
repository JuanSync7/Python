import os
import sys
import re
from textwrap import fill
from typing import Optional, List, Union
   
class StringUtil:
    """
    A comprehensive utility class for string manipulation and formatting with various decorations.
    Provides methods for text formatting, case conversion, wrapping, and visual elements.
    
    Features:
    - Text decoration (headers, underlines, boxes)
    - Case conversion (snake_case, CamelCase)
    - Text wrapping and formatting
    - Visual symbols and lines
    """
    styles = {
        'single': {
            'tl': '\u250C',  # ┌ (Top-left corner)
            'tr': '\u2510',  # ┐ (Top-right corner)
            'bl': '\u2514',  # └ (Bottom-left corner)
            'br': '\u2518',  # ┘ (Bottom-right corner)
            'h': '\u2500',   # ─ (Horizontal line)
            'v': '\u2502',  # │ (Vertical line)
            'j': '\u253C',   # ┼ (Junction/cross)
            'lh': '\u251C',  # ├ (Left T-junction)
            'rh': '\u2524',  # ┤ (Right T-junction)
            'th': '\u252C',  # ┬ (Top T-junction)
            'bh': '\u2534',  # ┴ (Bottom T-junction)
            'vh': '\u253C'   # ┼ (Same as 'j', cross)
        },
        'double': {
            'tl': '\u2554',  # ╔ (Top-left corner, double)
            'tr': '\u2557',  # ╗ (Top-right corner, double)
            'bl': '\u255A',  # ╚ (Bottom-left corner, double)
            'br': '\u255D',  # ╝ (Bottom-right corner, double)
            'h': '\u2550',  # ═ (Horizontal line, double)
            'v': '\u2551',  # ║ (Vertical line, double)
            'j': '\u256C',  # ╬ (Junction/cross, double)
            'lh': '\u2560',  # ╠ (Left T-junction, double)
            'rh': '\u2563',  # ╣ (Right T-junction, double)
            'th': '\u2566',  # ╦ (Top T-junction, double)
            'bh': '\u2569',  # ╩ (Bottom T-junction, double)
            'vh': '\u256C'   # ╬ (Same as 'j', cross)
        },
        'bold': {
            'tl': '\u250F',  # ┏ (Top-left corner, bold)
            'tr': '\u2513',  # ┓ (Top-right corner, bold)
            'bl': '\u2517',  # ┗ (Bottom-left corner, bold)
            'br': '\u251B',  # ┛ (Bottom-right corner, bold)
            'h': '\u2501',   # ━ (Horizontal line, bold)
            'v': '\u2503',  # ┃ (Vertical line, bold)
            'j': '\u254B',  # ╋ (Junction/cross, bold)
            'lh': '\u2523',  # ┣ (Left T-junction, bold)
            'rh': '\u252B',  # ┫ (Right T-junction, bold)
            'th': '\u2533',  # ┳ (Top T-junction, bold)
            'bh': '\u253B',  # ┻ (Bottom T-junction, bold)
            'vh': '\u254B'   # ╋ (Same as 'j', cross)
        },
        'round': {
            'tl': '\u256D',  # ╭ (Top-left corner, round)
            'tr': '\u256E',  # ╮ (Top-right corner, round)
            'bl': '\u2570',  # ╰ (Bottom-left corner, round)
            'br': '\u256F',  # ╯ (Bottom-right corner, round)
            'h': '\u2500',   # ─ (Same as 'single' horizontal)
            'v': '\u2502',   # │ (Same as 'single' vertical)
            'j': '\u253C',   # ┼ (Same as 'single' cross)
            'lh': '\u251C',  # ├ (Same as 'single' left T)
            'rh': '\u2524',  # ┤ (Same as 'single' right T)
            'th': '\u252C',  # ┬ (Same as 'single' top T)
            'bh': '\u2534',  # ┴ (Same as 'single' bottom T)
            'vh': '\u253C'   # ┼ (Same as 'j')
        },
        'ascii': {
            'tl': '+',  # + (Top-left, ASCII)
            'tr': '+',  # + (Top-right, ASCII)
            'bl': '+',  # + (Bottom-left, ASCII)
            'br': '+',  # + (Bottom-right, ASCII)
            'h': '-',   # - (Horizontal line, ASCII)
            'v': '|',   # | (Vertical line, ASCII)
            'j': '+',   # + (Junction, ASCII)
            'lh': '+',  # + (Left T, ASCII)
            'rh': '+',  # + (Right T, ASCII)
            'th': '+',  # + (Top T, ASCII)
            'bh': '+',  # + (Bottom T, ASCII)
            'vh': '+'   # + (Same as 'j')
        }
    }
    
    def __init__(
        self,
        default_length: int = 100,
        default_symbol: str = '-',
        default_style: str = 'single',
        default_header_level: int = 1,
        line_ending: str = '\n',
        comment_prefix: str = '#',
        **kwargs
    ):
        """
        Initialize StringUtil with default formatting options.
        
        Args:
            default_length: Default line length for wrapping and symbols
            default_symbol: Default symbol character for lines/underlines
            default_header_level: Default header level (1-6)
            line_ending: Line ending style ('\n' or '\r\n')
            comment_prefix: Prefix used for comment-style formatting
        """
        self.default_length = default_length
        self.default_symbol = default_symbol
        self.default_style = default_style
        self.default_header_level = default_header_level
        self.line_ending = line_ending
        self.comment_prefix = comment_prefix
        
        self.force_ascii = kwargs.pop('force_ascii', None)
        if self.force_ascii is None:
            # Auto-detect Unicode support
            self.force_ascii = not self._check_unicode_support()

        # Validate parameters
        if not 1 <= default_header_level <= 6:
            raise ValueError("Header level must be between 1 and 6")
        if line_ending not in ('\n', '\r\n'):
            raise ValueError("Line ending must be either '\\n' or '\\r\\n'")

    @staticmethod
    def _check_unicode_support() -> bool:
        """Check if the environment supports Unicode box characters"""
        # Check terminal capabilities
        if os.name == 'posix':
            # On Linux/Unix, check TERM and LC_* variables
            term = os.environ.get('TERM', '')
            if term.lower() in ('dumb', 'linux'):
                return False
            if 'C' in os.environ.get('LC_ALL', '') + os.environ.get('LC_CTYPE', ''):
                return False
        
        # Check if we're running in a known CI environment that might not handle Unicode well
        if os.environ.get('CI', '').lower() in ('true', '1'):
            return False
            
        # Check Python's stdout encoding
        try:
            if sys.stdout.encoding.lower() in ('ascii', 'ansi_x3.4-1968'):
                return False
        except:
            pass
            
        return True

    def underline(
        self,
        msg: str = '',
        symbol: Optional[str] = None,
        with_backslash: bool = False,
        comment_prefix: str = '#',
        with_comment_prefix: bool = True,
        newline: bool = True 
    ) -> str:
        """
        Underlines a message with a symbol line, with better control over spacing.
        
        Args:
            msg: The text to underline
            symbol: Character used for underline (default: instance default_symbol)
            with_backslash: Adds backslash at end if True
            comment_prefix: Prefix for comment-style formatting
            with_comment_prefix: Whether to include comment prefix
            newline: Whether to add trailing newline (default: True)
            
        Returns:
            Formatted string with underlined text
        """

        symbol = 'ascii' if self.force_ascii else (symbol if symbol is not None else self.default_style)
        
        comment_prefix = comment_prefix if comment_prefix is not None else self.comment_prefix
        
        # Define style mapping
        style_symbols = {
            'single': '\u2500',  # ─
            'double': '\u2550',  # ═
            'bold': '\u2501',    # ━
            'ascii': '-'   # -
        }
        
        # Get the appropriate symbol character
        symbol_char = style_symbols.get(symbol, symbol) 
        
        # Create the underline string
        underline = symbol_char * len(msg)
        
        # Build the lines
        if with_comment_prefix:
            lines = [
                f"{comment_prefix} {msg}",
                f"{comment_prefix} {underline}"
            ]
        else:
            lines = [
                msg,
                underline
            ]
        
        # Add backslashes if needed
        if with_backslash:
            lines = [f"{line} \\" for line in lines]
        
        # Join lines with line ending
        result = self.line_ending.join(lines)
        
        # Add trailing newline if requested
        if newline:
            result += self.line_ending
        
        return result
          
    def header(
            self,
            msg: str = '',
            with_backslash: bool = False,
            level: Optional[int] = None,
            newline: bool = True
        ) -> str:
            """
            Creates a header with the message surrounded by '#' characters.
            
            Example:
                header("Section", level=2) returns:
                ## Section ##
            
            Args:
                msg: The header text
                with_backslash: Adds backslash at end if True
                level: Header level (1-6, default: instance default_header_level)
            
            Returns:
                Formatted header string
            """
            level = level if level is not None else self.default_header_level
            
            suffix = ''
            if newline:
                suffix = (' \\' if with_backslash else '') + self.line_ending * 2
            else:
                suffix = ' \\' if with_backslash else ''

            return self.comment_prefix * level + ' ' + msg + ' ' + self.comment_prefix * level + suffix
          
        
    def close_header(
            self,
            msg: str = '',
            symbol: Optional[str] = None,
            length: Optional[int] = None,
            with_backslash: bool = False,
            level: Optional[int] = None,
            count_len: bool = False,
            newline: bool = True
        ) -> str:
            """
            Creates a closed box around the message with symbols.
            
            Example:
                close_header("Warning", symbol='*', length=30) returns:
                # **************************** #
                #          Warning             #
                # **************************** #
            
            Args:
                msg: The text to enclose
                symbol: Character used for borders (default: instance default_symbol)
                length: Total length of box (default: instance default_length)
                with_backslash: Adds backslashes at line ends if True
                level: Header level (1-6, default: instance default_header_level)
                count_len: Adjusts length to message length if True
            
            Returns:
                Formatted boxed header string
            """
            level = level if level is not None else self.default_header_level
            symbol = symbol if symbol is not None else self.default_symbol
            length = length if length is not None else self.default_length
            
            if level < 1:
                raise ValueError("Level must be at least 1.")
            
            if count_len:
                length = len(msg) + (level-1)*2
            else:
                msg_length = len(msg)
                total_length_with_hashes = msg_length + (level * 2)
                if total_length_with_hashes > length:
                    length = total_length_with_hashes
                
                # Calculate centering padding
                total_space = length - msg_length
                left_pad = total_space // 2
                right_pad = total_space - left_pad
            

            # Common prefix for 'middle' (with or without padding)
            middle_prefix = "#" * level + ' '
            middle_msg = (
                msg if count_len 
                else ' ' * left_pad + msg + ' ' * right_pad
            )
            middle_suffix = ' ' + "#" * level

            # Construct 'middle' based on 'with_backslash'
            if with_backslash:
                middle = middle_prefix + middle_msg + middle_suffix + ' \\' + self.line_ending
            else:
                middle = middle_prefix + middle_msg + middle_suffix + self.line_ending

            # Construct 'line' (repeated logic)
            line = self.comment_prefix + ' ' + symbol * length + ' #'
            if with_backslash:
                line += ' \\' + self.line_ending
            else:
                line += self.line_ending

            # Final return with optional newline
            if newline:
                return line + middle + line + ('\\' + self.line_ending if with_backslash else self.line_ending)
            else:
                return line + middle + line + ('\\' if with_backslash else '')

    def text_box(
        self,
        text: str,
        style: str = "single",
        padding: int = 1,
        margin: int = 0,
        align: str = "left",
        width: Optional[int] = None,
        # New parameters for code blocks
        language: str = "",
        syntax_highlight: bool = False,
        highlight_rules: Optional[dict] = None
    ) -> str:
        """
        Enhanced text_box with code block support.
        
        Args:
            text: The text to put in the box.
            style: Border style ('single', 'double', 'round', 'bold', 'ascii').
            padding: Number of spaces inside the box borders.
            margin: Number of spaces outside the box.
            align: Text alignment ('left', 'center', 'right').
            width: Fixed width for the box (None for auto-width).
            language: Language label for code blocks (e.g., "python", "bash").
            syntax_highlight: Enable basic syntax highlighting.
            highlight_rules: Custom syntax rules {token: color_code}.
            
        Returns:
            String with the text inside a box.
            
        Example:
            >> su = StringUtil()
            >> print(su.text_box("Hello", style="double", language="python"))
            ╔══ PYTHON ══════════════════════════════════╗
            ║   Hello                                    ║
            ╚════════════════════════════════════════════╝
        """
        
        style = 'ascii' if self.force_ascii else (style if style is not None else self.default_style)
        if style not in self.styles:
            raise ValueError(f"Invalid style. Choose from: {', '.join(self.styles.keys())}")
        
        chars = self.styles[style]
        lines = text.split('\n')
        
        # Apply syntax highlighting if enabled
        if syntax_highlight:
            highlight_rules = highlight_rules or self._get_default_highlight_rules(language)
            lines = [self._apply_syntax_highlight(line, highlight_rules) for line in lines]
        
        # Calculate visible width of text (accounting for special characters)
        def visible_width(s):
            # Remove ANSI color codes for width calculation
            return len(re.sub(r'\033\[[0-9;]*m', '', s))
        
        # Calculate box width
        if width is None:
            box_width = max(visible_width(line) for line in lines) + padding * 2 + 2  # +2 for borders
        else:
            box_width = width
        
        # Add language label if specified
        if language:
            label = f" {language.upper()} "
            label_line = (chars['h'] * 2) + label + (chars['h'] * (box_width - len(label) - 4))
            top_border = f"{' ' * margin}{chars['tl']}{label_line}{chars['tr']}"
        else:
            top_border = f"{' ' * margin}{chars['tl']}{chars['h'] * (box_width - 2)}{chars['tr']}"
        
        # Align each line
        content_lines = []
        for line in lines:
            visible_len = visible_width(line)
            content_width = box_width - 2 - padding * 2  # Total width minus borders and padding
            
            if align == 'left':
                aligned = line.ljust(content_width + (len(line) - visible_len))
            elif align == 'right':
                aligned = line.rjust(content_width + (len(line) - visible_len))
            else:  # center
                aligned = line.center(content_width + (len(line) - visible_len))
            
            padding_space = ' ' * padding
            content_lines.append(f"{' ' * margin}{chars['v']}{padding_space}{aligned}{padding_space}{chars['v']}")
        
        bottom_border = f"{' ' * margin}{chars['bl']}{chars['h'] * (box_width - 2)}{chars['br']}"
        
        return '\n'.join([top_border] + content_lines + [bottom_border])

    def table(
            self,
            headers: List[str],
            rows: List[List[str]],
            col_widths: Optional[List[int]] = None,
            style: str = "single",
            align: Union[str, List[str]] = "center",
            padding: int = 1,
            header_style: Optional[str] = None
        ) -> str:
        """
        Creates a table using box-drawing characters with customizable borders.
        
        Args:
            headers: List of column headers.
            rows: List of rows (each row is a list of strings).
            style: Border style ('single', 'double', 'bold', 'round', 'ascii').
            align: Alignment for columns ('left', 'center', 'right') as single value
                or list specifying alignment for each column.
            padding: Number of spaces inside each cell (default: 1).
            header_style: Optional different style for header separator.
                        If None, uses same style as rest of table.
        
        Returns:
            Formatted box-drawing table as string.
            
        Raises:
            ValueError: For invalid styles, alignments, or mismatched column counts.
            
        Example:
            >> string_util.table(["Name", "Age"], [["Alice", "30"], ["Bob", "25"]], "double")
            ╔═══════╦═════╗
            ║ Name  ║ Age ║
            ╠═══════╬═════╣
            ║ Alice ║ 30  ║
            ║ Bob   ║ 25  ║
            ╚═══════╩═════╝
        """
        style = 'ascii' if self.force_ascii else (style if style is not None else self.default_style)
        
        if style not in self.styles:
            raise ValueError(f"Invalid style. Choose from: {', '.join(self.styles.keys())}")
        chars = self.styles[style]
        header_chars = self.styles[header_style] if header_style else chars
        
        # Process alignment
        align_map = {'left': '<', 'center': '^', 'right': '>'}
        
        if isinstance(align, str):
            if align not in align_map:
                raise ValueError("Alignment must be 'left', 'center', or 'right'.")
            aligns = [align_map[align]] * len(headers)
        else:
            if len(align) != len(headers):
                raise ValueError("Number of alignments must match number of headers.")
            aligns = []
            for a in align:
                if a not in align_map:
                    raise ValueError("Alignment must be 'left', 'center', or 'right'.")
                aligns.append(align_map[a])
        
        # Validate row lengths
        for row in rows:
            if len(row) != len(headers):
                raise ValueError("All rows must have same length as headers.")
        
        # Calculate column widths
        all_cells = [headers] + rows
            # Replace automatic width calculation with:
        if col_widths is None:
            col_widths = [
                max(len(str(cell)) for cell in col)
                for col in zip(*([headers] + rows))
            ]
        
        # Build horizontal borders
        def make_border(left, middle, right, horizontal, widths):
            segments = [horizontal * (w + padding * 2) for w in widths]
            return left + middle.join(segments) + right
        
        top_border = make_border(chars['tl'], chars['th'], chars['tr'], chars['h'], col_widths)
        header_separator = make_border(header_chars['lh'], header_chars['vh'], header_chars['rh'], 
                                    header_chars['h'], col_widths)
        bottom_border = make_border(chars['bl'], chars['bh'], chars['br'], chars['h'], col_widths)
        
        # Build content rows
        def build_row(cells, widths, aligns):
            padded = [
                f"{str(cell):{align}{width + padding * 2}}"
                for cell, align, width in zip(cells, aligns, widths)
            ]
            return chars['v'] + chars['v'].join(padded) + chars['v']
        
        header_row = build_row(headers, col_widths, aligns)
        data_rows = [build_row(row, col_widths, aligns) for row in rows]
        
        # Combine all parts
        return '\n'.join(
            [top_border, header_row, header_separator] +
            data_rows +
            [bottom_border]
        )
        
    def _apply_syntax_highlight(self, line: str, rules: dict) -> str:
        """Applies syntax highlighting to a single line"""
        for pattern, color in rules.items():
            line = re.sub(pattern, f"{color}\\g<0>\033[0m", line)
        return line

    def _strip_ansi(self, text: str) -> str:
        """Removes ANSI color codes for width calculation"""
        return re.sub(r'\033\[[0-9;]*m', '', text)

    # Helper methods for syntax highlighting
    def _get_default_highlight_rules(self, language: str) -> dict:
        """Returns default syntax highlighting rules for common languages"""
        rules = {
            'python': {
                '#.*': '\033[32m',  # Comments in green
                'def|class|import|from': '\033[34m',  # Keywords in blue
                '".*?"': '\033[33m'  # Strings in yellow
            },
            'bash': {
                '#.*': '\033[32m',
                'sudo|apt|yum|brew': '\033[31m',
                '".*?"': '\033[33m'
            }
        }
        return rules.get(language.lower(), {})

    def line(
        self,
        symbol: Optional[str] = None,
        length: Optional[int] = None,
        comment_prefix: str = "#",
        with_backslash: bool = False,
        with_comment_prefix: bool = True,
        newline: bool = False
    ) -> str:
        """
        Draws a horizontal symbol line.
        
        Args:
            symbol: Character used for line (default: instance default_symbol)
            length: Line length (default: instance default_length)
            with_backslash: Adds backslash at end if True
            no_space: Omits extra newline if True
        
        Returns:
            Formatted symbol line
        """
        symbol = symbol if symbol is not None else self.default_symbol
        length = length if length is not None else self.default_length
        comment_prefix = comment_prefix if comment_prefix is not None else self.comment_prefix
        
        if with_backslash:
            return comment_prefix + ' ' + symbol * length + ' ' + comment_prefix + ' \\' + self.line_ending + ('\\' + self.line_ending) * (newline)
        else: 
            return comment_prefix + ' ' + symbol * length + ' ' + comment_prefix + self.line_ending + self.line_ending * (newline)
            
    def wrap_text(
        self,
        text: str,
        length: Optional[int] = None,
        prefix: Optional[str] = None
    ) -> str:
        """
        Wraps text to specified length with optional prefix on each line.
        
        Args:
            text: Input text to wrap
            length: Maximum line length (default: instance default_length)
            prefix: Line prefix (default: instance comment_prefix)
        
        Returns:
            Wrapped text with prefixes
        """
        length = length if length is not None else self.default_length
        prefix = prefix if prefix is not None else self.comment_prefix
        return fill(text, length=length - len(prefix), initial_indent=prefix, subsequent_indent=prefix)
        
    def to_snake_case(self, text: str) -> str:
        """
        Converts CamelCase or space-separated strings to snake_case.
        
        Example:
            "CamelCaseString" -> "camel_case_string"
            "Some Text" -> "some_text"
        
        Args:
            text: Input string to convert
        
        Returns:
            snake_case formatted string
        """
        # Handle space-separated strings first
        text = text.replace(' ', '_')
        # Convert CamelCase to snake_case
        text = re.sub('([a-z0-9])([A-Z])', r'\1_\2', text)
        return text.lower()

    def to_camel_case(self, text: str) -> str:
        """
        Converts snake_case or space-separated strings to CamelCase.
        
        Example:
            "snake_case_string" -> "SnakeCaseString"
            "some text" -> "SomeText"
        
        Args:
            text: Input string to convert
        
        Returns:
            CamelCase formatted string
        """
        # Remove any existing spaces/underscores and capitalize each word
        return ''.join(word.title() for word in re.split(r'[ _]', text))

    def to_kebab_case(self, text: str) -> str:
        """
        Converts strings to kebab-case.
        
        Example:
            "Some Text" -> "some-text"
            "camelCaseString" -> "camel-case-string"
        
        Args:
            text: Input string to convert
        
        Returns:
            kebab-case formatted string
        """
        # Convert to snake_case first, then replace underscores with hyphens
        snake = self.to_snake_case(text)
        return snake.replace('_', '-')

    def strip_comments(self, text: str, comment_prefix: Optional[str] = None) -> str:
        """
        Removes comment lines (starting with comment_prefix) from text.
        
        Args:
            text: Input text with possible comments
        
        Returns:
            Text with comment lines removed
        """
        comment_prefix = comment_prefix if comment_prefix is not None else self.comment_prefix
        
        return self.line_ending.join(
            line for line in text.split(self.line_ending)
            if not line.lstrip().startswith(comment_prefix)
        )

    def align_columns(self, rows: List[List[str]], padding: int = 2) -> str:
        """
        Formats text into aligned columns.
        
        Args:
            rows: List of rows (each row is list of columns)
            padding: Spaces between columns
        
        Returns:
            String with aligned columns
        """
        if not rows:
            return ''
            
        # Calculate max width for each column
        col_widths = [
            max(len(str(item)) for item in column)
            for column in zip(*rows)
        ]
        
        # Format each row with padding
        return self.line_ending.join(
            ' '.join(
                str(item).ljust(width + padding)
                for item, width in zip(row, col_widths)
            )
            for row in rows
        )

    def progress_bar(
        self,
        current: int,
        total: int,
        length: int = 50,
        fill_char: str = '=',
        empty_char: str = ' ',
        brackets: str = '[]'
    ) -> str:
        """
        Generates a text progress bar.
        
        Args:
            current: Current progress value
            total: Total value for completion
            length: Character length of bar
            fill_char: Character for filled portion
            empty_char: Character for empty portion
            brackets: Start/end bracket characters
        
        Returns:
            Formatted progress bar string
        """
        if len(brackets) != 2:
            raise ValueError("Brackets must be exactly 2 characters")
            
        progress = min(max(current / total, 0), 1)
        filled = int(length * progress)
        bar = fill_char * filled + empty_char * (length - filled)
        return f"{brackets[0]}{bar}{brackets[1]} {int(progress * 100)}%"
    

    def table_to_html(self, table: str) -> str:
        """Converts box-drawing table to HTML (basic implementation)."""
        lines = table.split('\n')
        if len(lines) < 3:
            return ""

        # Extract headers and rows
        headers = [h.strip() for h in lines[1].split('│')[1:-1]]
        rows = []
        for line in lines[3:-1]:
            rows.append([cell.strip() for cell in line.split('│')[1:-1]])

        # Generate HTML
        html = ['<table border="1">']
        html.append('  <thead><tr>')
        for header in headers:
            html.append(f'    <th>{header}</th>')
        html.append('  </tr></thead>')
        html.append('  <tbody>')
        for row in rows:
            html.append('    <tr>')
            for cell in row:
                html.append(f'      <td>{cell}</td>')
            html.append('    </tr>')
        html.append('  </tbody>')
        html.append('</table>')
        return '\n'.join(html)
    
    def horizontal_line(
        self,
        style: str = "single",
        length: int = 20,
        margin: int = 0
    ) -> str:
        """
        Creates a horizontal line using box-drawing characters.
        
        Args:
            style: Line style ('single', 'double', 'bold', 'ascii').
            length: Length of the line.
            margin: Left margin spaces.
            
        Returns:
            Horizontal line string.
            
        Example:
            >> su.horizontal_line('double', 10)
            '════════════'
        """
        styles = {
            'single': '─',
            'double': '═',
            'bold': '━',
            'ascii': '-',
        }
        
        style = style if not None else self.default_style if not self.force_ascii else 'ascii' 
        
        if style not in styles:
            raise ValueError(f"Invalid style. Choose from: {', '.join(styles.keys())}")
            
        return (' ' * margin) + (styles[style] * length)
    
if __name__ == '__main__':
    string_util = StringUtil()

    # Basic table
    print(string_util.table(["Name", "Age"], [["Alice", "30"], ["Bob", "25"]]))

    # Double border with left-aligned
    print(string_util.table(
        ["ID", "Description", "Price"],
        [["1", "Widget", "$10.99"], ["2", "Gadget", "$24.95"]],
        style="double",
        align="left"
    ))

    # Mixed alignment with bold borders
    print(string_util.table(
        ["Product", "Stock", "Price"],
        [["Apples", "100", "$1.99"], ["Oranges", "75", "$2.49"]],
        style="bold",
        align=["left", "center", "right"]
    ))

    # Define the table data
    headers = ["Argument (-)", "Argument (--)", "Description", "Required?", "Data Type", "Default"]
    rows = [
        ["-h", "--help", "Shows the help message", "No", "N/A", "False"],
        ["-t", "--top", "Top module name", "Yes", "Text", "None"],
        ["-f", "--filelist", "Filelist format supported by questa", "Yes, if GUI disabled", "Path", "None"],
        ["-cp", "--comppath", "Component path used in .f files", "No", "Path", "None"],
        ["-g", "--gui", "Enable GUI mode", "No", "N/A", "False"],
        ["-l", "--lib", "Library", "No", "Text", "work"],
        ["-o", "--workdir", "Work directory output", "No", "Path", "workdir/"],
        ["-p", "--pref", "Tool preference commands", "No", "Path", "None"],
        ["-pf", "--pref_file", "Tool preference file", "No", "Path", "None"],  
        ["-do", "--dofile", "Custom do file post-analysis", "No", "Path", "None"],
        ["-opt", "--tool_opts", "Tool options file path", "No", "Path", "None"],
        ["-pre", "--prescript", "Custom prescript file", "No", "Path", "None"],
        ["-post", "--postscript", "Custom postscript file", "No", "Path", "None"],
        ["-db", "--database_file", "Database file", "No", "Path", "None"]
    ]

    # Generate the table with double borders and mixed alignment
    table = string_util.table(
        headers,
        rows,
        style="round",
        align=["left", "left", "left", "left", "left", "left"],
        padding=1,
        header_style="round"
    )
    
    print(table)