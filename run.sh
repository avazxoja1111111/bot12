#!/bin/bash

# Kitobxon Kids Educational Bot Startup Script
# Optimized for production deployment with monitoring and recovery

set -e  # Exit on any error

# Configuration
BOT_NAME="Kitobxon Kids Bot"
PYTHON_EXECUTABLE="python3"
MAIN_SCRIPT="main.py"
LOG_FILE="bot.log"
PID_FILE="bot.pid"
MAX_MEMORY_MB=1000
RESTART_DELAY=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Check if bot is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    else
        return 1
    fi
}

# Check system requirements
check_requirements() {
    log "🔍 Checking system requirements..."
    
    # Check Python version
    if ! command -v $PYTHON_EXECUTABLE &> /dev/null; then
        error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    local python_version=$($PYTHON_EXECUTABLE --version 2>&1 | cut -d' ' -f2)
    local major_version=$(echo $python_version | cut -d'.' -f1)
    local minor_version=$(echo $python_version | cut -d'.' -f2)
    
    if [ "$major_version" -lt 3 ] || [ "$major_version" -eq 3 -a "$minor_version" -lt 8 ]; then
        error "Python 3.8+ is required. Found: $python_version"
        exit 1
    fi
    
    info "Python version: $python_version ✅"
    
    # Check main script exists
    if [ ! -f "$MAIN_SCRIPT" ]; then
        error "Main script '$MAIN_SCRIPT' not found"
        exit 1
    fi
    
    # Check environment variables
    if [ -z "$BOT_TOKEN" ]; then
        error "BOT_TOKEN environment variable is required"
        exit 1
    fi
    
    info "Bot token configured ✅"
    
    # Check available memory
    if command -v free &> /dev/null; then
        local available_mb=$(free -m | awk 'NR==2{print $7}')
        if [ "$available_mb" -lt "$MAX_MEMORY_MB" ]; then
            warning "Low available memory: ${available_mb}MB (recommended: ${MAX_MEMORY_MB}MB+)"
        else
            info "Available memory: ${available_mb}MB ✅"
        fi
    fi
    
    # Check disk space
    local available_space=$(df . | tail -1 | awk '{print $4}')
    if [ "$available_space" -lt 1000000 ]; then  # Less than 1GB
        warning "Low disk space available"
    fi
    
    log "✅ System requirements check completed"
}

# Install/update dependencies
install_dependencies() {
    log "📦 Installing/updating dependencies..."
    
    # Check if virtual environment should be used
    if [ -d "venv" ] || [ -d ".venv" ]; then
        if [ -d "venv" ]; then
            source venv/bin/activate
        elif [ -d ".venv" ]; then
            source .venv/bin/activate
        fi
        info "Virtual environment activated"
    fi
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        $PYTHON_EXECUTABLE -m pip install --upgrade pip
        $PYTHON_EXECUTABLE -m pip install -r requirements.txt
        info "Dependencies installed from requirements.txt"
    elif [ -f "pyproject.toml" ]; then
        $PYTHON_EXECUTABLE -m pip install --upgrade pip
        $PYTHON_EXECUTABLE -m pip install .
        info "Dependencies installed from pyproject.toml"
    else
        warning "No dependency file found (requirements.txt or pyproject.toml)"
        # Install core dependencies
        $PYTHON_EXECUTABLE -m pip install aiogram openpyxl python-docx reportlab
        info "Core dependencies installed"
    fi
}

# Create necessary directories
setup_directories() {
    log "📁 Setting up directories..."
    
    # Create data directory
    mkdir -p bot_data
    mkdir -p temp_exports
    mkdir -p logs
    
    # Set permissions
    chmod 755 bot_data temp_exports logs
    
    info "Directories created: bot_data, temp_exports, logs"
}

# Start the bot
start_bot() {
    if is_running; then
        warning "Bot is already running (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    log "🚀 Starting $BOT_NAME..."
    
    # Start bot in background
    nohup $PYTHON_EXECUTABLE -u "$MAIN_SCRIPT" > "$LOG_FILE" 2>&1 &
    local bot_pid=$!
    
    # Save PID
    echo $bot_pid > "$PID_FILE"
    
    # Wait a moment and check if bot started successfully
    sleep 2
    if ps -p $bot_pid > /dev/null 2>&1; then
        log "✅ $BOT_NAME started successfully (PID: $bot_pid)"
        info "📋 Log file: $LOG_FILE"
        info "🆔 PID file: $PID_FILE"
        return 0
    else
        error "Failed to start $BOT_NAME"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Stop the bot
stop_bot() {
    if ! is_running; then
        warning "Bot is not running"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    log "🛑 Stopping $BOT_NAME (PID: $pid)..."
    
    # Try graceful shutdown first
    kill -TERM $pid 2>/dev/null || true
    
    # Wait for graceful shutdown
    local count=0
    while [ $count -lt 10 ] && ps -p $pid > /dev/null 2>&1; do
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    if ps -p $pid > /dev/null 2>&1; then
        warning "Graceful shutdown failed, forcing termination"
        kill -KILL $pid 2>/dev/null || true
        sleep 1
    fi
    
    # Clean up PID file
    rm -f "$PID_FILE"
    
    if ! ps -p $pid > /dev/null 2>&1; then
        log "✅ $BOT_NAME stopped successfully"
        return 0
    else
        error "Failed to stop $BOT_NAME"
        return 1
    fi
}

# Restart the bot
restart_bot() {
    log "🔄 Restarting $BOT_NAME..."
    stop_bot
    sleep $RESTART_DELAY
    start_bot
}

# Show bot status
status_bot() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        local uptime=$(ps -o etime= -p $pid 2>/dev/null | tr -d ' ')
        log "✅ $BOT_NAME is running (PID: $pid, Uptime: $uptime)"
        
        # Show memory usage if available
        if command -v ps &> /dev/null; then
            local memory_mb=$(ps -o rss= -p $pid 2>/dev/null | awk '{print int($1/1024)}')
            if [ ! -z "$memory_mb" ] && [ "$memory_mb" -gt 0 ]; then
                info "💾 Memory usage: ${memory_mb}MB"
                
                if [ "$memory_mb" -gt "$MAX_MEMORY_MB" ]; then
                    warning "High memory usage detected!"
                fi
            fi
        fi
    else
        warning "❌ $BOT_NAME is not running"
    fi
}

# Monitor bot and auto-restart if needed
monitor_bot() {
    log "👁️  Starting monitoring mode..."
    info "Press Ctrl+C to stop monitoring"
    
    local restart_count=0
    local max_restarts=5
    local monitor_interval=30
    
    while true; do
        if ! is_running; then
            if [ $restart_count -lt $max_restarts ]; then
                warning "Bot not running, attempting restart ($((restart_count + 1))/$max_restarts)"
                if start_bot; then
                    restart_count=0
                    log "✅ Bot restarted successfully"
                else
                    restart_count=$((restart_count + 1))
                    error "Failed to restart bot"
                    if [ $restart_count -ge $max_restarts ]; then
                        error "Maximum restart attempts reached. Stopping monitor."
                        break
                    fi
                fi
            else
                error "Maximum restart attempts reached. Bot may have a persistent issue."
                break
            fi
        else
            # Check memory usage
            local pid=$(cat "$PID_FILE")
            if command -v ps &> /dev/null; then
                local memory_mb=$(ps -o rss= -p $pid 2>/dev/null | awk '{print int($1/1024)}')
                if [ ! -z "$memory_mb" ] && [ "$memory_mb" -gt $((MAX_MEMORY_MB * 2)) ]; then
                    warning "High memory usage detected (${memory_mb}MB), restarting bot"
                    restart_bot
                fi
            fi
        fi
        
        sleep $monitor_interval
    done
}

# View logs
view_logs() {
    if [ -f "$LOG_FILE" ]; then
        log "📋 Showing recent logs from $LOG_FILE"
        echo "----------------------------------------"
        tail -n 50 "$LOG_FILE"
        echo "----------------------------------------"
        info "Use 'tail -f $LOG_FILE' to follow logs in real-time"
    else
        warning "Log file not found: $LOG_FILE"
    fi
}

# Clean up old files
cleanup() {
    log "🧹 Cleaning up old files..."
    
    # Clean old log files (keep last 5)
    if ls logs/*.log >/dev/null 2>&1; then
        ls -t logs/*.log | tail -n +6 | xargs rm -f 2>/dev/null || true
    fi
    
    # Clean temp files older than 1 day
    find temp_exports -type f -mtime +1 -delete 2>/dev/null || true
    
    # Clean up any orphaned PID files
    if [ -f "$PID_FILE" ] && ! is_running; then
        rm -f "$PID_FILE"
    fi
    
    info "Cleanup completed"
}

# Show help
show_help() {
    echo -e "${BLUE}$BOT_NAME Management Script${NC}"
    echo
    echo "Usage: $0 {start|stop|restart|status|monitor|logs|cleanup|install|help}"
    echo
    echo "Commands:"
    echo "  start     - Start the bot"
    echo "  stop      - Stop the bot"
    echo "  restart   - Restart the bot"
    echo "  status    - Show bot status"
    echo "  monitor   - Monitor bot and auto-restart if needed"
    echo "  logs      - View recent logs"
    echo "  cleanup   - Clean up old files"
    echo "  install   - Install/update dependencies"
    echo "  help      - Show this help message"
    echo
    echo "Environment Variables:"
    echo "  BOT_TOKEN        - Telegram bot token (required)"
    echo "  SUPER_ADMIN_ID   - Super admin user ID (optional)"
    echo
    echo "Examples:"
    echo "  $0 start          # Start the bot"
    echo "  $0 monitor        # Start with monitoring"
    echo "  BOT_TOKEN=your_token $0 start  # Start with token"
}

# Main execution
main() {
    case "$1" in
        start)
            check_requirements
            setup_directories
            start_bot
            ;;
        stop)
            stop_bot
            ;;
        restart)
            restart_bot
            ;;
        status)
            status_bot
            ;;
        monitor)
            check_requirements
            setup_directories
            if ! is_running; then
                start_bot || exit 1
            fi
            monitor_bot
            ;;
        logs)
            view_logs
            ;;
        cleanup)
            cleanup
            ;;
        install)
            install_dependencies
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}Received interrupt signal${NC}"; exit 0' INT

# Run main function with all arguments
main "$@"
