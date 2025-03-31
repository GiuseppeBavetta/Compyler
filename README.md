# Compyler - Python to Executable Converter GUI

Compyler is a user-friendly graphical interface for Nuitka, a Python to executable converter that compiles Python code into standalone executables. This tool makes it easy to convert your Python scripts into distributable applications without needing to use the command line.

> **Note:** This project is based on [Nuitka](https://nuitka.net/), a powerful Python compiler. Compyler is simply a GUI wrapper that makes Nuitka more accessible to users who prefer graphical interfaces over command-line tools. All the actual compilation work is done by Nuitka itself.

## Features

- **Intuitive GUI**: Simple and straightforward interface for selecting and compiling Python scripts
- **Compilation Options**: Multiple configuration options organized in tabs including:
  - Mode options (standalone, onefile, module)
  - Optimization settings (Link-time optimization, parallel jobs)
  - GUI application settings (console visibility, custom icons)
  - Advanced custom options
- **Real-time Progress**: See compilation progress with estimated time remaining
- **Interactive Terminal**: Built-in terminal for viewing compilation output
- **Command History**: Navigate through previous commands with up/down arrows
- **Built-in Snake Game**: Play Snake while waiting for your compilation to finish
- **Success Notifications**: Clear indication when compilation is successful with direct access to the compiled executable



## Requirements

- Python 3.6 or higher
- Nuitka package (`pip install nuitka`)
- Tkinter (usually comes with Python installation)

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/compyler.git
```

2. Install the required dependencies:
```
pip install nuitka
```

3. Run the application:
```
python compyler.py
```

## Usage

1. Click "Browse..." to select your Python script
2. Select your desired output directory
3. Configure compilation options in the tabs
4. Click "Compile with Nuitka" to start the compilation
5. Enjoy a game of Snake while you wait for compilation to complete
6. When compilation finishes, you can directly open the output folder or access your compiled executable

### Terminal Commands

The built-in terminal supports various commands:
- `clear`: Clear the terminal
- `help`: Show help information
- `status`: Show compilation status
- `version`: Check the installed Nuitka version

You can also run any system command directly in the terminal.

## Compilation Options

### Mode
- **Standalone**: Create a standalone package that includes all dependencies
- **Onefile**: Combine everything into a single executable file
- **Module**: Compile as a Python extension module
- **Follow Imports**: Automatically include imported modules
- **No Follow Imports**: Don't automatically include imports

### Optimization
- **Link Time Optimization (LTO)**: Enable link-time optimization
- **Parallel Jobs**: Use multiple processors for compilation (configurable)

### GUI
- **Disable Console**: Hide console window when the application runs
- **Tkinter Support**: Enable support for Tkinter GUI applications
- **Custom Icon**: Use a custom icon for the compiled executable

### Advanced
- Enter custom Nuitka command-line options for advanced users

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is released under the Public Domain for free reuse. You are free to use, modify, distribute, and perform the work [not for commercial purposes].

## Acknowledgements

- [Nuitka](https://nuitka.net/) - The Python compiler that does all the actual work

## About Nuitka

Nuitka is the Python compiler this GUI is built around. It's an excellent tool that:

- Compiles Python code to C code and then to executable binaries
- Supports all Python versions including 2.6, 2.7, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, and 3.11
- Allows creating standalone applications that include all dependencies
- Works on Windows, macOS and Linux
- Is actively maintained with regular updates

Please visit the [official Nuitka website](https://nuitka.net/) for more information about the compiler, its capabilities, and documentation.
