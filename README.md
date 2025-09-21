# Super-Gemini 🚀

✨ Super-Gemini is a **local-first, agentic AI system** that runs on Android through Termux, providing powerful terminal emulation and extensive Linux package management capabilities.  
✦ It acts as a **universal developer + productivity agent**, automating tasks, scaffolding web applications, and controlling your development environment.

<div align="center">

```
   _____                          _____                _       _ 
  / ____|                        / ____|              (_)     (_)
 | (___  _   _ _ __   ___ _ __  | |  __  ___ _ __ ___  _ _ __  _ 
  \___ \| | | | '_ \ / _ \ '__| | | |_ |/ _ \ '_ ` _ \| | '_ \| |
  ____) | |_| | |_) |  __/ |    | |__| |  __/ | | | | | | | | | |
 |_____/ \__,_| .__/ \___|_|     \_____|\___|_| |_| |_|_|_| |_|_|
              | |                                                
              |_|                                                
```

</div>

## 🌟 Key Features

### 🤖 Local-First AI Agent Execution
- Runs completely on your device - no cloud dependency
- Powered by local language models
- Secure and privacy-focused operation
- Real-time task planning and execution

### 🔄 Multi-Runtime Support
- **Bash**: System automation and shell scripting
- **Python**: AI, data processing, and backend logic
- **Node.js**: Web development and JavaScript tooling
- Seamless integration between runtimes

### 🏗️ Web Application Scaffolding
- Quick-start templates for modern frameworks:
  - React for interactive UIs
  - Next.js for full-stack applications
  - Svelte for lightweight apps
  - Laravel for PHP backends
- Automated project setup and configuration
- Best practices and patterns built-in

### 📱 Android/Termux Integration
- Native Android UI with Material Design
- Termux-based Linux environment
- Optional Ubuntu environment via proot-distro
- Full development environment on mobile
- Seamless desktop-mobile workflow

### 🧠 Persistent Memory Management
- JSON-based vector store for knowledge
- Long-term context retention
- User preferences and settings
- Efficient embedding-based search

### 🧪 Comprehensive Testing
- Automated test suites for all components
- Runtime validation scripts
- Integration tests for Android
- CI/CD pipeline ready

## 🚀 Installation Options

### Quick Setup (Basic)
1. Install [Termux from F-Droid](https://f-droid.org/en/packages/com.termux/)
2. Run the setup script:
   ```bash
   curl -sL https://raw.githubusercontent.com/codedwithlikhon/Super-Gemini/main/setup.sh | bash
   ```

### Enhanced Setup (with Ubuntu)
1. Complete the Quick Setup first
2. Install Ubuntu environment:
   ```bash
   curl -sL https://raw.githubusercontent.com/codedwithlikhon/Super-Gemini/main/setup_ubuntu.sh | bash
   ```

### Manual Installation
1. Update Termux:
   ```bash
   pkg update -y && pkg upgrade -y
   ```

2. Install core dependencies:
   ```bash
   pkg install -y git python nodejs sqlite curl wget
   ```

3. Clone and setup:
   ```bash
   git clone https://github.com/codedwithlikhon/Super-Gemini.git
   cd Super-Gemini
   pip install -r tools/requirements.txt
   ```

## 🎯 Getting Started

1. Launch Super-Gemini:
   ```bash
   cd ~/Super-Gemini && python main.py
   ```

2. Start coding! Try these commands:
   - "Create a new Next.js project"
   - "Set up a Python Flask API"
   - "Run tests for the current project"

3. For Ubuntu environment (optional):
   ```bash
   proot-distro login ubuntu
   ```

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Usage Tutorial](docs/usage.md)
- [Development Roadmap](docs/roadmap.md)

## 🛠️ Development

Super-Gemini follows these core principles:
- **Modularity**: Each component is self-contained
- **Extensibility**: Easy to add new tools and capabilities
- **Security**: Local-first, permission-based access
- **Performance**: Optimized for mobile devices

## 🤝 Contributing

We welcome contributions! Please check our [Contributing Guidelines](CONTRIBUTING.md) before getting started.

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 🔗 Quick Links

- [Report Bug](https://github.com/codedwithlikhon/Super-Gemini/issues)
- [Request Feature](https://github.com/codedwithlikhon/Super-Gemini/issues/new)
- [Documentation](docs/)
