import re
from typing import List, Tuple, Union,Optional

class MarkDown:
    """
    A utility class for generating Markdown formatted text with various formatting options.
    
    This class provides methods to create common Markdown elements like bold/italic text,
    tables, lists, code blocks, links, images, and more complex structures like tables of contents.
    """

    def __init__(
        self,
        default_align: str = "left",
        default_header_level: int = 1,
        default_list_indent: int = 2,
        enable_emoji: bool = True,
        strict_mode: bool = False,
        line_ending: str = "\n"
    ):
        """
        Initialize MarkDown generator with configuration options.
        
        Args:
            default_align: Default table alignment ('left', 'center', 'right')
            default_header_level: Default header level (1-6)
            default_list_indent: Default indentation spaces for nested lists
            enable_emoji: Whether to enable emoji support
            strict_mode: Whether to enforce strict CommonMark compliance
            line_ending: Line ending style ('\n' or '\r\n')
        """
        self.default_align = default_align
        self.default_header_level = default_header_level
        self.default_list_indent = default_list_indent
        self.enable_emoji = enable_emoji
        self.strict_mode = strict_mode
        self.line_ending = line_ending
        
        # Validation
        if self.default_header_level not in range(1, 7):
            raise ValueError("Header level must be between 1 and 6")
        if self.line_ending not in ("\n", "\r\n"):
            raise ValueError("Line ending must be either '\\n' or '\\r\\n'")
    
    def bold(self, text: str) -> str:
        """Wraps text in Markdown bold syntax.
        
        Args:
            text: The text to be bolded.
            
        Returns:
            The text wrapped in double asterisks for bold formatting.
            
        Example:
            >> md = MarkDown()
            >> md.bold("important")
            '**important**'
        """
        return f"**{text}**"

    def italic(self, text: str) -> str:
        """Wraps text in Markdown italic syntax.
        
        Args:
            text: The text to be italicized.
            
        Returns:
            The text wrapped in single asterisks for italic formatting.
            
        Example:
            >> md.italic("emphasis")
            '*emphasis*'
        """
        return f"*{text}*"

    def bold_italic(self, text: str) -> str:
        """Wraps text in bold + italic syntax.
        
        Args:
            text: The text to be formatted with both bold and italic.
            
        Returns:
            The text wrapped in triple asterisks for bold and italic formatting.
            
        Example:
            >> md.bold_italic("very important")
            '***very important***'
        """
        return f"***{text}***"
    
    def header(self, text: str, level: Optional[int] = None) -> str:
        """Creates a Markdown header using instance default level if none specified.
        
        Args:
            text: The header text.
            level: Header level (1-6).
            
        Returns:
            Formatted Markdown header.
            
        Raises:
            ValueError: If level is not between 1 and 6.
            
        Example:
            >> md.header("Introduction", 2)
            '## Introduction'
        """
        if not 1 <= level <= 6:
            raise ValueError("Header level must be between 1 and 6")
        return f"{'#' * level} {text}"
    
    def table(
            self,
            headers: List[str],
            rows: List[List[str]],
            align: Union[str, List[str]] = None
        ) -> str:
        """
        Generates a Markdown table with specified headers, rows, and alignment.
        
        Args:
            headers: List of column headers.
            rows: List of rows (each row is a list of strings).
            align: Alignment for columns ('left', 'center', 'right') as a single value
                for all columns or a list specifying alignment for each column.
        
        Returns:
            Formatted Markdown table as a string.
            
        Raises:
            ValueError: If alignment is invalid or column counts don't match.
            
        Example:
            >>> md.table(["Name", "Age"], [["Alice", "30"], ["Bob", "25"]], "center")
            '| Name  | Age |\n|:-----:|:---:|\n| Alice | 30  |\n| Bob   | 25  |'
        """
        
        align = align or self.default_align
        
        # Validate alignment
        align_map = {"left": ":--", "center": ":--:", "right": "--:"}
        
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
        for i, row in enumerate(rows, 1):
            if len(row) != len(headers):
                raise ValueError(f"Row {i} has {len(row)} columns, expected {len(headers)}")
        
        # Build header and separator
        header_line = "| " + " | ".join(headers) + " |"
        separator = "|" + "|".join(aligns) + "|"  # More compact
        
        # Build rows with proper spacing
        row_lines = []
        for row in rows:
            # Pad each cell with spaces for better readability
            padded_row = [f" {cell.strip()} " for cell in row]
            row_lines.append("|" + "|".join(padded_row) + "|")
        
        return "\n".join([header_line, separator] + row_lines)
    
    def generate_toc(
        self,
        headers: List[Tuple[int, str]],
        max_depth: int = 3
    ) -> str:
        """
        Generates a Markdown table of contents from headers.
        
        Args:
            headers: List of tuples (level, text), e.g., [(1, "Introduction")].
                    Level should indicate header level (1 for #, 2 for ##, etc.)
            max_depth: Maximum header level to include (e.g., 3 for ###).
        
        Returns:
            TOC as a nested bullet list in Markdown format.
            
        Example:
            >> headers = [(1, "Intro"), (2, "Features"), (3, "Installation")]
            >> md.generate_toc(headers)
            '- [Intro](#intro)\\n  - [Features](#features)\\n    - [Installation](#installation)'
        """
        toc = []
        for level, text in headers:
            if level > max_depth:
                continue
            indent = "  " * (level - 1)
            anchor = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
            toc.append(f"{indent}- [{text}](#{anchor})")
        return "\n".join(toc)
    
    def bullet_list(self, items: List[str], indent: Optional[int] = None) -> str:
        """Converts a list of strings into a Markdown bullet list using instance default indentation if none specified.
        
        Args:
            items: List of strings to convert to bullet points.
            indent: Number of indentation levels (each level is 2 spaces).
            
        Returns:
            String with each item as a bullet point.
            
        Example:
            >> md.bullet_list(["apple", "banana", "cherry"], 1)
            '  - apple\\n  - banana\\n  - cherry'
        """
        indent = indent if indent is not None else self.default_list_indent
        indent_str = "  " * indent
        return self.line_ending.join(f"{indent_str}- {item}" for item in items)

    def numbered_list(self, items: List[str], start: int = 1) -> str:
        """Converts a list of strings into a Markdown numbered list.
        
        Args:
            items: List of strings to convert to numbered list.
            start: Starting number for the list.
            
        Returns:
            String with each item as a numbered point.
            
        Example:
            >> md.numbered_list(["First", "Second", "Third"])
            '1. First\\n2. Second\\n3. Third'
        """
        return "\n".join(f"{i}. {item}" for i, item in enumerate(items, start))
    
    def horizontal_rule(self, style: str = "---", length: int = 3) -> str:
        """Inserts a Markdown horizontal rule.
        
        Args:
            style: Style of rule ('---', '***', or '___').
            length: Number of characters to use (minimum 3).
            
        Returns:
            Horizontal rule string.
            
        Raises:
            ValueError: If style is invalid or length is too short.
            
        Example:
            >> md.horizontal_rule("***", 5)
            '*****'
        """
        valid_styles = ["---", "***", "___"]
        if style not in valid_styles:
            raise ValueError(f"Style must be one of: {valid_styles}")
        if length < 3:
            raise ValueError("Length must be at least 3 characters.")
        return style[0] * length
    
    def inline_code(self, text: str) -> str:
        """Wraps text in inline code syntax.
        
        Args:
            text: The text to format as inline code.
            
        Returns:
            The text wrapped in backticks.
            
        Example:
            >> md.inline_code("print('hello')")
            '`print(\'hello\')`'
        """
        return f"`{text}`"

    def code_block(self, code: str, language: str = "") -> str:
        """Wraps text in a Markdown code block with optional language.
        
        Args:
            code: The code to format.
            language: Optional language for syntax highlighting.
            
        Returns:
            The code wrapped in triple backticks with language specification.
            
        Example:
            >> md.code_block("print('hello')", "python")
            '```python\\nprint(\'hello\')\\n```'
        """
        return f"```{language}{self.line_ending}{code}{self.line_ending}```"
    
    def link(self, text: str, url: str, title: str = "") -> str:
        """Creates a Markdown hyperlink.
        
        Args:
            text: The link text to display.
            url: The URL to link to.
            title: Optional title text for the link.
            
        Returns:
            Markdown formatted link.
            
        Example:
            >> md.link("Google", "https://google.com", "Search engine")
            '[Google](https://google.com "Search engine")'
        """
        if title:
            return f'[{text}]({url} "{title}")'
        return f"[{text}]({url})"

    def image(self, alt_text: str, image_url: str, title: str = "") -> str:
        """Embeds an image in Markdown.
        
        Args:
            alt_text: Alternative text for the image.
            image_url: URL of the image.
            title: Optional title text for the image.
            
        Returns:
            Markdown formatted image tag.
            
        Example:
            >> md.image("Logo", "logo.png", "Company Logo")
            '![Logo](logo.png "Company Logo")'
        """
        if title:
            return f'![{alt_text}]({image_url} "{title}")'
        return f"![{alt_text}]({image_url})"
    
    def footnote(self, text: str, ref: str = "") -> str:
        """Adds a footnote with an optional reference ID.
        
        Args:
            text: The text to footnote.
            ref: Optional reference ID. If not provided, one is generated.
            
        Returns:
            Text with footnote reference.
            
        Example:
            >> md.footnote("More information available", "info")
            'More information available[^info]'
        """
        ref = ref or str(hash(text))  # Auto-generate a unique ref if none provided
        return f"{text}[^{ref}]"

    def footnote_reference(self, ref: str, note: str) -> str:
        """Defines the footnote reference at the bottom of the document.
        
        Args:
            ref: The reference ID used in the footnote.
            note: The footnote text.
            
        Returns:
            Markdown formatted footnote definition.
            
        Example:
            >> md.footnote_reference("info", "See our website for details")
            '[^info]: See our website for details'
        """
        return f"[^{ref}]: {note}"
    
    def collapse_section(self, summary: str, details: str) -> str:
        """Creates a collapsible section (uses HTML <details> tag).
        
        Note: This uses HTML tags which may not render in all Markdown viewers.
        
        Args:
            summary: The text shown when collapsed.
            details: The content shown when expanded.
            
        Returns:
            HTML details element as string.
            
        Example:
            >> md.collapse_section("Click to expand", "Hidden content")
            '<details><summary>Click to expand</summary>\\n\\nHidden content\\n\\n</details>'
        """
        if self.strict_mode:
            return f"{summary}{self.line_ending}{details}"
        return f"<details><summary>{summary}</summary>{self.line_ending}{self.line_ending}{details}{self.line_ending}{self.line_ending}</details>"
    
    def checkbox_list(self, items: List[Tuple[str, bool]]) -> str:
        """Creates a Markdown checklist.
        
        Args:
            items: List of tuples (text, checked) where checked is boolean.
            
        Returns:
            Markdown formatted checklist.
            
        Example:
            >> items = [("Buy milk", False), ("Walk dog", True)]
            >> md.checkbox_list(items)
            '- [ ] Buy milk\\n- [x] Walk dog'
        """
        return "\n".join(
            f"- [{'x' if checked else ' '}] {text}"
            for text, checked in items
        )
        
    def escape_markdown(self, text: str) -> str:
        """Escapes Markdown special characters (e.g., *, _, `, []).
        
        Args:
            text: The text to escape.
            
        Returns:
            Text with Markdown special characters escaped.
            
        Example:
            >> md.escape_markdown("This *is* important_")
            'This \\*is\\* important\\_'
        """
        if self.strict_mode:
            # More comprehensive escaping in strict mode
            return re.sub(r"([\\`*_{}\[\]()#+-.!])", r"\\\1", text)
        # Basic escaping in non-strict mode
        return re.sub(r"([*_`\[\]])", r"\\\1", text)
    
    def latex_equation(self, equation: str, inline: bool = False) -> str:
        """Formats LaTeX equations for Markdown.
        
        Args:
            equation: The LaTeX equation to format.
            inline: Whether to format as inline (single $) or block (double $$).
            
        Returns:
            Markdown formatted LaTeX equation.
            
        Example:
            >> md.latex_equation("\\frac{1}{2}", inline=True)
            '$\\frac{1}{2}$'
        """
        if inline:
            return f"${equation}$"
        else:
            return f"$$\n{equation}\n$$"
        
    def multi_column_list(self, items: List[str], columns: int = 2) -> str:
        """Formats items into a multi-column table (for GitHub comments).
        
        Args:
            items: List of strings to format into columns.
            columns: Number of columns to create.
            
        Returns:
            Markdown table with items distributed across columns.
            
        Example:
            >> items = ["Apple", "Banana", "Cherry", "Date"]
            >> md.multi_column_list(items, 2)
            '| Apple   | Banana  |\\n| Cherry  | Date    |'
        """
        if columns < 1:
            raise ValueError("Columns must be at least 1")
            
        # Calculate column width based on longest item
        col_width = max((len(item) for item in items), default=0) + 2
        rows = [items[i:i+columns] for i in range(0, len(items), columns)]
        
        # Pad each item to equal width
        formatted_rows = []
        for row in rows:
            padded_row = [item.ljust(col_width) for item in row]
            formatted_rows.append("| " + " | ".join(padded_row) + " |")
            
        return "\n".join(formatted_rows)
        
    def csv_to_markdown_table(self, csv_data: str, delimiter: str = ",") -> str:
        """Converts CSV data to a Markdown table.
        
        Args:
            csv_data: String containing CSV data.
            delimiter: Character used to separate fields in CSV.
            
        Returns:
            Markdown formatted table.
            
        Example:
            >> csv = "Name,Age\\Juan,30\\nChee,25"
            >> md.csv_to_markdown_table(csv)
            '| Name | Age |\\n|-------|-----|\\n| Juan | 30 |\\n| Chee | 25 |'
        """
        lines = [line.strip() for line in csv_data.strip().split("\n") if line.strip()]
        if not lines:
            return ""
            
        headers = lines[0].split(delimiter)
        rows = [line.split(delimiter) for line in lines[1:]]
        return self.table(headers, rows)
    
    def blockquote(self, text: str, level: int = 1) -> str:
        """Formats text as a Markdown blockquote.
        
        Args:
            text: The text to format as a blockquote.
            level: Nesting level (1 for single >, 2 for >>, etc.)
            
        Returns:
            Text formatted as a blockquote.
            
        Example:
            >> md.blockquote("This is important", 2)
            '>> This is important'
        """
        if level < 1:
            raise ValueError("Level must be at least 1")
        quote_symbol = ">" * level
        # Split lines and add quote symbol to each line
        lines = text.split("\n")
        return "\n".join(f"{quote_symbol} {line}" for line in lines)
    
    def strikethrough(self, text: str) -> str:
        """Formats text with strikethrough.
        
        Args:
            text: The text to strike through.
            
        Returns:
            Text wrapped in double tildes for strikethrough.
            
        Example:
            >> md.strikethrough("old price")
            '~~old price~~'
        """
        return f"~~{text}~~"
    
    def task_list(self, items: List[Tuple[str, bool]]) -> str:
        """Creates a GitHub-flavored Markdown task list.
        
        Args:
            items: List of tuples (text, completed) where completed is boolean.
            
        Returns:
            Markdown formatted task list.
            
        Example:
            >> tasks = [("Fix bug", True), ("Add tests", False)]
            >> md.task_list(tasks)
            '- [x] Fix bug\\n- [ ] Add tests'
        """
        return self.checkbox_list(items)
    
    def mention_user(self, username: str) -> str:
        """Creates a user mention (GitHub/GitLab flavor).
        
        Args:
            username: The username to mention.
            
        Returns:
            Formatted user mention.
            
        Example:
            >> md.mention_user("octocat")
            '@octocat'
        """
        return f"@{username}"
    
    def emoji(self, emoji_name: str) -> str:
        """Inserts a GitHub-flavored Markdown emoji.
        
        Args:
            emoji_name: The name of the emoji (e.g., 'smile').
            
        Returns:
            Formatted emoji.
            
        Example:
            >> md.emoji("rocket")
            ':rocket:'
        """
        if not self.enable_emoji:
            if self.strict_mode:
                return self.escape_markdown(f":{emoji_name}:")
            return f":{emoji_name}:"
        return f":{emoji_name}:"
        
    
if __name__ == '__main__':
    md = MarkDown()
    
    # Generate README.md content
    readme_content = [
        md.header("Questa QC wrapper script", 1),
        "",
        "This script is made to execute Questa Lint and CDC/RDC jobs using LSF.",
        md.header("Getting started", 2),
        "To facilitate your onboarding with Questa QC wrapper script, please refer to the following sections.",
        "",
        md.checkbox_list([
            ("Usage", True),
            ("Examples", True),
            ("Templates", True)
        ]),
        "",
        md.header("Usage", 2),
        "Positional Arguments are required. There are 1 positional arguments currently required.",
        "",
        md.table(
            headers=["Positional Arguments", "Description", "Required?", "Data Type", "Default"],
            rows=[
                [
                    "subparser_name", 
                    "specify the flow to run. The 3 options are: lint, cdc and rdc", 
                    "yes", 
                    "string", 
                    "None"
                ]
            ],
            align="left"
        ),
        "",
        md.code_block("usage: lint <common_arguments> <specific_arguments>\n"
                     "or: cdc <common_arguments> <specific_arguments>\n"
                     "or: rdc <common_arguments> <specific_arguments>", "text"),
        "",
        md.header("Common Arguments", 2),
        md.table(
            headers=["Short Option", "Long Option", "Description", "Required?", "Data Type", "Default"],
            rows=[
                ["`-h`", "`--help`", "Shows the help message", "No", "N/A", "`False`"],
                ["`-t`", "`--top`", "Top module name", "Yes", "Text", "`None`"],
                ["`-f`", "`--filelist`", "Filelist format supported by questa", "Yes (if GUI disabled)", "Path", "`None`"],
                ["`-cp`", "`--comppath`", "Component path used in .f files gen by febuild", "No", "Path", "`None`"],
                ["`-g`", "`--gui`", "Enable gui mode by adding this argument", "No", "N/A", "`False`"],
                ["`-l`", "`--lib`", "Library", "No", "Text", "`oc_libVlog`"],
                ["`-o`", "`--workdir`", "Workdir output directory", "No", "Path", "`workdir/`"],
                ["`-p`", "`--pref`", "Tool preference or do commands for pre-analysis", "No", "Path", "`None`"],
                ["`-pf`", "`--pref_file`", "Tool preference or do file for pre-analysis", "No", "Path", "`None`"],
                ["`-do`", "`--dofile`", "Custom do file post analysis", "No", "Path", "`None`"],
                ["`-opt`", "`--tool_opts`", "Tool options file path", "No", "Path", "`None`"],
                ["`-pre`", "`--prescript`", "Custom prescript csh file", "No", "Path", "`None`"],
                ["`-post`", "`--postscript`", "Custom postscript csh file", "No", "Path", "`None`"],
                ["`-db`", "`--database_file`", "The database_file", "No", "Path", "`None`"]
            ],
            align="left"
        ),
        "",
        md.header("Lint Specific Arguments", 2),
        md.header("Overview", 3),
        "This section showcase the available positional and optional arguments available under the lint tool flow.",
        md.header("Lint Specific Command Examples", 4),
        md.code_block("./questa_run lint {<Common_Arguments> <lint_specific_commands}", "text"),
        "",
        md.header("Lint Optional Argument", 3),
        "The table below shows the available an extension of optional arguments that is available when the lint tool is specified.",
        md.table(
            headers=["Argument (-)", "Argument (--)", "Description", "Required?", "Data Type", "Default"],
            rows=[
                ["-ext", "--external", "Define component is from external source", "No", "N/A", "False"],
                ["-cc", "--compile_cmd", "A vlog/vcom compile option file", "No", "Path", "None"],
                ["-w", "--waiver", "Lint Waiver File", "No", "Path", "None"],
                ["-incr", "--incremental", "Specify lint run is an incremental run", "No", "N/A", "False"]
            ],
            align="left"
        ),
        "",
        md.header("Lint Positional Argument", 3),
        "The table below shows positional arguments that have further subcommands that run specific functions.",
        md.table(
            headers=["Positional Arguments", "Description", "Required?", "Data Type", "Default"],
            rows=[
                ["report", "Specify after lint to run some report commands.", "no", "string", "None"],
                ["fix", "Specify after lint to fix some lint violations.", "no", "string", "None"],
                ["setup", "Specify after lint to automatically setup lint directory.", "no", "string", "None"]
            ],
            align="left"
        ),
        "",
        md.header("Lint Subcommands Example", 4),
        md.code_block("./questa_run lint {<positional_argument} {<positional_argument_subcommands>}", "text"),
        "",
        md.header("CDC Specific Arguments", 2),
        md.table(
            headers=["Argument (-)", "Argument (--)", "Description", "Required?", "Data Type", "Default"],
            rows=[
                ["-c", "--cons", "Constraints file", "No", "Path", "None"],
                ["-s", "--sdc", "SDC Constraints file or .f constraints filelist", "No", "Path", "None"]
            ],
            align="left"
        ),
        "",
        md.header("RDC Specific Arguments", 2),
        md.table(
            headers=["Argument (-)", "Argument (--)", "Description", "Required?", "Data Type", "Default"],
            rows=[
                ["-c", "--cons", "Constraints file", "No", "Path", "None"],
                ["-s", "--sdc", "SDC Constraints file or .f constraints filelist", "No", "Path", "None"]
            ],
            align="left"
        ),
        "",
        md.header("Examples", 2),
        md.code_block("lint -t <top_module> -cc <vlog_compile> -p <pre_analysis_script> -pre <prescript> -do <do_file> -I \n"
                     "cdc -f <filelist> -t <top_module> -c <constraint_file> -fd <file_directory> -opt <tool_opts> -o <output_dir>", "text"),
        "",
        md.header("Full Documentation at:", 2),
        md.code_block("https://openchip.atlassian.net/wiki/spaces/SH/pages/268599322/Lint+Flow", "text"),
        "",
        md.header("Example 1", 3),
        md.code_block("./questa_run cdc -f VtPcl/shared/vt_src_open-full_pkg.f -t VtPcl -c VtPcl/shared/blocks/VtPcl/constraints/VtPcl.sdc -fd /ln/proj/va_10/a0/workareas/TEMP/VT_PCL_JAN_2025/vt_pcl_20250127_33a7a9dd7b4/sim/src -opt questa_run/templates/tool_opts -p questa_run/templates/pref.do -do questa_run/templates/dofile.do -o questa_work", "text"),
        "",
        md.header("Example 2", 3),
        md.code_block("./questa_run -cdc -f pcl/design/units/Pcl/sim/vt_sanitychk_rtl/vt_src_open-full_pkg.f pcl/design/units/Pcl/sim/vt_sanitychk_rtl/ip_stub_src_pkg.f -t VtPcl -fd pcl/design/units/Pcl/sim/vt_sanitychk_rtl/ -opt questa_run/templates/tool_opts -p questa_run/templates/pref.do -do questa_run/templates/dofile.do -post questa_run/templates/postscript.csh -o questa_work_hier", "text"),
        "",
        md.header("Example 3", 3),
        md.code_block("./questa_run lint -t VtPcl -o questa_work -g", "text"),
        "",
        md.header("Example 4", 3),
        md.code_block("./questa_run lint -t VtPcl -cc compile_vl -p templates/lint_setup.do -pre templates/lint_pre.do -do templates/lint_post.do -I", "text"),
        "",
        md.header("Templates", 2),
        "Note: If you need to add paths in the following input files, be sure to specify them as absolute paths, since the working directory will change to {workdir}/{top}/{lint cdc rdc} as defined in the arguments.",
        md.header("tool_opts", 3),
        md.code_block("vcom=>-64 -quiet\nvlog=>-suppress vlog-2583 -svinputport=relaxed\ncdc run=>-report_modes\nbsub=>-q pa -I", "text"),
        "",
        md.header("prescript.csh", 3),
        md.code_block("echo \"Starting...\"", "bash"),
        "",
        md.header("pref.do", 3),
        md.code_block("#cdc preference -sdc_sta_mode;\n#sdc preference -infer_false_path_domains;\n#sdc preference -sta_mode;\n#sdc load /ln/proj/va_10/a0/workareas/z2youkassou/VtPcl/shared/blocks/VtPcl/constraints/VtPcl.sdc;\ndo /ln/proj/va_10/a0/workareas/z2youkassou/VtPcl/shared/cdc.tcl;\nhier block VtCpu;\ncdc methodology soc -goal release;", "tcl"),
        "",
        md.header("dofile.do", 3),
        md.code_block("sdc generate tcl cdc.tcl\ncdc generate html html_dashboard\ncdc generate tree clock_tree.rpt -clock \ncdc generate tree reset_tree.rpt -reset\nreport directives", "text"),
        "",
        md.header("postscript.csh", 3),
        md.code_block("echo \"Starting HDM Top-Down CDC Analysis...\"\nmake -f Results/hcdc_run.Makefile all\necho \"Finished!\"", "bash")
    ]
    
    # Join all sections with line endings
    full_readme = md.line_ending.join(readme_content)
    
    # Write to README.md file
    with open("README.md", "w") as f:
        f.write(full_readme)
    
    print("README.md generated successfully!")

