# Deployment Guide for Gearhead Assist

## Overview

Gearhead Assist requires Ollama to run the custom `gearhead3.1:8b` model. Since Streamlit Community Cloud doesn't support Ollama, you need to run Ollama on a separate server and connect to it remotely.

## Architecture

```
[Streamlit Cloud App] <--HTTPS--> [Your Ollama Server]
                                   (running gearhead3.1:8b model)
```

## Deployment Options

### Option 1: Run Ollama on Your Local Machine (Development/Testing)

**Pros:**
- Free
- Quick setup
- Full control

**Cons:**
- Your computer must be running 24/7
- Requires exposing your machine to the internet (security risk)
- Not recommended for production

**Setup:**

1. **Install and configure Ollama:**
   ```bash
   # Start Ollama with external access
   OLLAMA_HOST=0.0.0.0:11434 ollama serve
   ```

2. **Expose port 11434 using ngrok or similar:**
   ```bash
   # Install ngrok: https://ngrok.com/
   ngrok http 11434
   ```

3. **Set environment variable in Streamlit Cloud:**
   - Go to your Streamlit Cloud app settings
   - Add secret: `OLLAMA_HOST = "https://your-ngrok-url.ngrok.io"`

### Option 2: Run Ollama on a Cloud VM (Recommended for Production)

**Pros:**
- Always available
- More secure
- Better performance
- Can scale

**Cons:**
- Costs money ($5-20/month depending on provider)

**Recommended Providers:**
- **DigitalOcean** ($4-6/month for basic droplet)
- **Linode/Akamai** ($5/month)
- **AWS Lightsail** ($5/month)
- **Vultr** ($6/month)
- **Hetzner** (cheapest, ~€4/month)

**Setup Steps:**

1. **Create a VM instance:**
   - Choose Ubuntu 22.04 or later
   - Minimum: 2GB RAM, 2 vCPUs
   - Recommended: 4GB RAM, 2 vCPUs for better performance

2. **Install Ollama on the VM:**
   ```bash
   # SSH into your VM
   curl -fsSL https://ollama.com/install.sh | sh
   ```

3. **Upload your Modelfile:**
   ```bash
   # From your local machine
   scp Modelfile user@your-vm-ip:~/
   ```

4. **Create the gearhead3.1:8b model:**
   ```bash
   # On the VM
   ollama create gearhead3.1:8b -f ~/Modelfile
   ```

5. **Configure Ollama to accept external connections:**
   ```bash
   # Create systemd override
   sudo mkdir -p /etc/systemd/system/ollama.service.d
   sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null <<EOF
   [Service]
   Environment="OLLAMA_HOST=0.0.0.0:11434"
   EOF

   # Restart Ollama
   sudo systemctl daemon-reload
   sudo systemctl restart ollama
   ```

6. **Set up HTTPS with Nginx (Recommended for Security):**
   ```bash
   # Install Nginx and Certbot
   sudo apt update
   sudo apt install -y nginx certbot python3-certbot-nginx

   # Configure Nginx as reverse proxy
   sudo tee /etc/nginx/sites-available/ollama > /dev/null <<'EOF'
   server {
       listen 80;
       server_name your-domain.com;  # Replace with your domain

       location / {
           proxy_pass http://localhost:11434;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   EOF

   # Enable the site
   sudo ln -s /etc/nginx/sites-available/ollama /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx

   # Get SSL certificate (requires a domain name)
   sudo certbot --nginx -d your-domain.com
   ```

7. **Configure firewall:**
   ```bash
   # Allow HTTP/HTTPS
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 22/tcp  # SSH
   sudo ufw enable
   ```

8. **Set environment variable in Streamlit Cloud:**
   - Go to your Streamlit Cloud app settings
   - Add secret: `OLLAMA_HOST = "https://your-domain.com"`
   - Or use IP: `OLLAMA_HOST = "http://your-vm-ip:11434"`

### Option 3: Use Ollama Cloud Service (When Available)

Ollama may release a cloud hosting service in the future. Check [ollama.com](https://ollama.com) for updates.

## Security Considerations

### If using HTTP (without SSL):
⚠️ **Not recommended for production**

### If using HTTPS (with SSL):
✅ **Recommended**

### Additional Security:
1. **API Key Authentication** (coming soon to Ollama)
2. **IP Whitelisting** - Restrict access to Streamlit Cloud IPs
3. **VPN/Tailscale** - Create private network between VM and Streamlit app

## Testing the Connection

Test your Ollama server is accessible:

```bash
# From any machine
curl http://your-ollama-host:11434/api/tags

# Should return JSON with your models
```

## Streamlit Cloud Configuration

1. **Go to** [share.streamlit.io](https://share.streamlit.io)
2. **Deploy your app** from GitHub
3. **Add Secret:**
   - Go to App Settings → Secrets
   - Add:
     ```toml
     OLLAMA_HOST = "https://your-ollama-server.com"
     ```
4. **Reboot the app**

## Cost Estimate

### Minimum Setup (Testing):
- VM: $5/month
- Domain (optional): $12/year
- SSL Certificate: Free (Let's Encrypt)
- **Total: ~$5-6/month**

### Recommended Setup:
- VM with 4GB RAM: $12/month
- Domain: $12/year
- SSL Certificate: Free
- **Total: ~$13/month**

## Alternative: Use OpenAI or Anthropic API

If you don't want to manage infrastructure, consider using:
- OpenAI GPT-4 with custom instructions
- Anthropic Claude with custom system prompt
- Replicate for hosted open-source models

This requires rewriting the Ollama integration but works directly on Streamlit Cloud.

## Monitoring

Monitor your Ollama server:
```bash
# Check if Ollama is running
systemctl status ollama

# View logs
journalctl -u ollama -f

# Check resource usage
htop
```

## Troubleshooting

### Connection Refused
- Check firewall rules
- Verify Ollama is listening on 0.0.0.0
- Test with curl locally first

### Model Not Found
- Verify model is created: `ollama list`
- Recreate model: `ollama create gearhead3.1:8b -f Modelfile`

### Slow Response
- Increase VM resources
- Check network latency
- Consider using a faster model or quantization
