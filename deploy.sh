#!/bin/bash

# Script di deployment per Dashboard Gestione CPA
# Esegui questo script su un server Linux per deployare l'applicazione

set -e

# Configurazione
APP_NAME="cpa-dashboard"
APP_USER="www-data"
APP_DIR="/opt/cpa-dashboard"
SERVICE_NAME="cpa-dashboard"
NGINX_SITE="cpa-dashboard"

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funzioni di utilità
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Controllo privilegi root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Questo script deve essere eseguito come root"
        exit 1
    fi
}

# Aggiornamento sistema
update_system() {
    log_info "Aggiornamento sistema..."
    apt update && apt upgrade -y
}

# Installazione dipendenze
install_dependencies() {
    log_info "Installazione dipendenze di sistema..."
    
    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        nginx \
        git \
        curl \
        unzip \
        sqlite3
}

# Creazione utente applicazione
create_app_user() {
    log_info "Creazione utente applicazione..."
    
    if ! id "$APP_USER" &>/dev/null; then
        useradd -r -s /bin/false -d "$APP_DIR" "$APP_USER"
        log_info "Utente $APP_USER creato"
    else
        log_info "Utente $APP_USER già esistente"
    fi
}

# Clone/aggiornamento repository
setup_application() {
    log_info "Setup applicazione..."
    
    if [ ! -d "$APP_DIR" ]; then
        git clone https://github.com/yourusername/Dashboard_Gestione_CPA.git "$APP_DIR"
        log_info "Repository clonato in $APP_DIR"
    else
        cd "$APP_DIR"
        git pull origin main
        log_info "Repository aggiornato"
    fi
    
    # Permessi directory
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    chmod -R 755 "$APP_DIR"
}

# Setup ambiente Python
setup_python_env() {
    log_info "Setup ambiente Python..."
    
    cd "$APP_DIR"
    
    # Creazione ambiente virtuale
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_info "Ambiente virtuale creato"
    fi
    
    # Attivazione e installazione dipendenze
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Creazione directory necessarie
    mkdir -p data exports logs backups
    chown -R "$APP_USER:$APP_USER" data exports logs backups
}

# Configurazione systemd service
setup_systemd_service() {
    log_info "Configurazione systemd service..."
    
    cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=CPA Dashboard
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Ricarica systemd
    systemctl daemon-reload
    
    # Abilita e avvia service
    systemctl enable "$SERVICE_NAME"
    systemctl start "$SERVICE_NAME"
    
    log_info "Service $SERVICE_NAME configurato e avviato"
}

# Configurazione Nginx
setup_nginx() {
    log_info "Configurazione Nginx..."
    
    # Crea configurazione sito
    cat > "/etc/nginx/sites-available/$NGINX_SITE" << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }

    # Log personalizzati
    access_log /var/log/nginx/cpa-dashboard-access.log;
    error_log /var/log/nginx/cpa-dashboard-error.log;
}
EOF

    # Abilita sito
    ln -sf "/etc/nginx/sites-available/$NGINX_SITE" "/etc/nginx/sites-enabled/"
    
    # Test configurazione
    nginx -t
    
    # Riavvia Nginx
    systemctl restart nginx
    
    log_info "Nginx configurato"
}

# Configurazione firewall
setup_firewall() {
    log_info "Configurazione firewall..."
    
    # Abilita UFW se disponibile
    if command -v ufw &> /dev/null; then
        ufw allow 22/tcp    # SSH
        ufw allow 80/tcp    # HTTP
        ufw allow 443/tcp   # HTTPS
        ufw --force enable
        log_info "Firewall UFW configurato"
    else
        log_warning "UFW non disponibile, configura manualmente il firewall"
    fi
}

# Configurazione SSL con Let's Encrypt
setup_ssl() {
    log_info "Configurazione SSL con Let's Encrypt..."
    
    # Installa Certbot
    apt install -y certbot python3-certbot-nginx
    
    log_info "Certbot installato. Per ottenere un certificato SSL, esegui:"
    log_info "certbot --nginx -d your-domain.com"
}

# Configurazione backup automatico
setup_backup() {
    log_info "Configurazione backup automatico..."
    
    # Crea script di backup
    cat > "$APP_DIR/backup.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python -c "
from utils.backup import create_backup
success, result = create_backup()
print(f'Backup: {result}')
"
EOF

    chmod +x "$APP_DIR/backup.sh"
    chown "$APP_USER:$APP_USER" "$APP_DIR/backup.sh"
    
    # Crea cron job per backup giornaliero
    (crontab -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh >> $APP_DIR/logs/backup.log 2>&1") | crontab -
    
    log_info "Backup automatico configurato (giornaliero alle 2:00)"
}

# Configurazione log rotation
setup_log_rotation() {
    log_info "Configurazione log rotation..."
    
    cat > "/etc/logrotate.d/$SERVICE_NAME" << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $APP_USER $APP_USER
    postrotate
        systemctl reload $SERVICE_NAME
    endscript
}
EOF

    log_info "Log rotation configurato"
}

# Test applicazione
test_application() {
    log_info "Test applicazione..."
    
    # Attendi che l'applicazione sia pronta
    sleep 5
    
    # Test connessione
    if curl -s http://localhost:8501 > /dev/null; then
        log_info "Applicazione funzionante su http://localhost:8501"
    else
        log_error "Applicazione non raggiungibile"
        systemctl status "$SERVICE_NAME"
        exit 1
    fi
}

# Mostra informazioni finali
show_final_info() {
    log_info "Deployment completato con successo!"
    echo
    echo "📊 Dashboard Gestione CPA"
    echo "========================"
    echo "📍 Directory applicazione: $APP_DIR"
    echo "👤 Utente applicazione: $APP_USER"
    echo "🔧 Service: $SERVICE_NAME"
    echo "🌐 Nginx: configurato"
    echo "📱 Porta applicazione: 8501"
    echo "🌍 URL pubblico: http://$(hostname -I | awk '{print $1}')"
    echo
    echo "📋 Comandi utili:"
    echo "  Status service: systemctl status $SERVICE_NAME"
    echo "  Riavvia service: systemctl restart $SERVICE_NAME"
    echo "  Log applicazione: journalctl -u $SERVICE_NAME -f"
    echo "  Log Nginx: tail -f /var/log/nginx/cpa-dashboard-*.log"
    echo
    echo "🔒 Per SSL/HTTPS, esegui:"
    echo "  certbot --nginx -d your-domain.com"
    echo
    echo "📁 Backup automatici configurati per le 2:00 del mattino"
}

# Funzione principale
main() {
    log_info "🚀 Avvio deployment Dashboard Gestione CPA..."
    
    check_root
    update_system
    install_dependencies
    create_app_user
    setup_application
    setup_python_env
    setup_systemd_service
    setup_nginx
    setup_firewall
    setup_ssl
    setup_backup
    setup_log_rotation
    test_application
    show_final_info
    
    log_info "✅ Deployment completato!"
}

# Gestione errori
trap 'log_error "Deployment fallito. Controlla i log per dettagli."' ERR

# Esecuzione
main "$@"
