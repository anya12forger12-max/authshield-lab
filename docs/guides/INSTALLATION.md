# Installation Guide

This guide covers installing AuthShield Lab on Windows, Linux, and macOS.

## Prerequisites

Before installing AuthShield Lab, ensure you have the following:

| Prerequisite | Minimum Version | Recommended |
|-------------|----------------|-------------|
| Node.js | 18.0 | 20.x LTS |
| Python | 3.11 | 3.12 |
| pip | 23.0 | Latest |
| npm | 9.0 | 10.x |
| Git | 2.40 | Latest |

## Windows Installation

### Step 1: Install Node.js

Download and install Node.js 18+ from [nodejs.org](https://nodejs.org/). Select the LTS version.

Verify installation:

```cmd
node --version
npm --version
```

### Step 2: Install Python

Download and install Python 3.11+ from [python.org](https://www.python.org/downloads/). Check "Add Python to PATH" during installation.

Verify installation:

```cmd
python --version
pip --version
```

### Step 3: Install Git

Download and install Git from [git-scm.com](https://git-scm.com/).

Verify installation:

```cmd
git --version
```

### Step 4: Clone the Repository

```cmd
git clone https://github.com/authshieldlab/authshield-lab.git
cd authshield-lab
```

### Step 5: Set Up Backend

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### Step 6: Set Up Frontend

```cmd
cd ..\frontend
npm install
copy .env.example .env
```

### Step 7: Initialize Database

```cmd
cd ..\backend
python -m app.database.init
```

### Step 8: Verify Installation

```cmd
cd ..
scripts\build\build.bat
```

## Linux Installation

### Step 1: Install Node.js

```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 20
nvm use 20

# Or using apt (Ubuntu/Debian)
sudo apt update
sudo apt install nodejs npm
```

Verify installation:

```bash
node --version
npm --version
```

### Step 2: Install Python

```bash
# Using apt (Ubuntu/Debian)
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Or using dnf (Fedora)
sudo dnf install python3.11 python3.11-pip
```

Verify installation:

```bash
python3 --version
pip3 --version
```

### Step 3: Install Git

```bash
# Using apt
sudo apt install git

# Using dnf
sudo dnf install git
```

Verify installation:

```bash
git --version
```

### Step 4: Clone the Repository

```bash
git clone https://github.com/authshieldlab/authshield-lab.git
cd authshield-lab
```

### Step 5: Set Up Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Step 6: Set Up Frontend

```bash
cd ../frontend
npm install
cp .env.example .env
```

### Step 7: Initialize Database

```bash
cd ../backend
python -m app.database.init
```

### Step 8: Verify Installation

```bash
cd ..
chmod +x scripts/build/build.sh
./scripts/build/build.sh
```

## macOS Installation

### Step 1: Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Node.js

```bash
brew install node@20
```

Verify installation:

```bash
node --version
npm --version
```

### Step 3: Install Python

```bash
brew install python@3.12
```

Verify installation:

```bash
python3 --version
pip3 --version
```

### Step 4: Install Git

```bash
brew install git
```

Verify installation:

```bash
git --version
```

### Step 5: Clone the Repository

```bash
git clone https://github.com/authshieldlab/authshield-lab.git
cd authshield-lab
```

### Step 6: Set Up Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Step 7: Set Up Frontend

```bash
cd ../frontend
npm install
cp .env.example .env
```

### Step 8: Initialize Database

```bash
cd ../backend
python -m app.database.init
```

### Step 9: Verify Installation

```bash
cd ..
chmod +x scripts/build/build.sh
./scripts/build/build.sh
```

## Running the Application

### Development Mode

```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### Production Mode

```bash
# Build the application
./scripts/build/build.sh  # Linux/macOS
scripts\build\build.bat    # Windows
```

## Troubleshooting

### Port Already in Use

If port 8000 is occupied:

```bash
# Find the process using the port
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Kill the process
kill <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows
```

### Python Virtual Environment Issues

```bash
# Remove and recreate
rm -rf venv  # Linux/macOS
rmdir /s /q venv  # Windows

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Node Modules Issues

```bash
# Clean install
rm -rf node_modules package-lock.json  # Linux/macOS
rmdir /s /q node_modules & del package-lock.json  # Windows

npm install
```

### Permission Errors (Linux/macOS)

```bash
# Fix npm permissions
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Python Module Not Found

Ensure the virtual environment is activated:

```bash
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
which python              # Should show venv path
```

## Next Steps

After installation, see:

- [Development Guide](DEVELOPMENT.md) for development setup
- [User Guide](USER_GUIDE.md) for using the platform
- [Administrator Guide](ADMINISTRATOR.md) for system administration
