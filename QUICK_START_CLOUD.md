# Quick Start: Deploy to Streamlit Cloud

## The Problem

You **cannot** package the Ollama model directly with your Streamlit app because:
- Streamlit Cloud doesn't support Docker/system services
- The model file is 2GB+ (too large for cloud deployment)
- Ollama requires special runtime environment

## The Solution

Run Ollama on a **separate server** and connect to it remotely.

```
┌─────────────────────┐         ┌──────────────────┐
│  Streamlit Cloud    │◄───────►│  Your Ollama     │
│  (Your App UI)      │  HTTPS  │  Server (Model)  │
└─────────────────────┘         └──────────────────┘
```

## Fastest Way to Get Started

### Step 1: Choose Your Ollama Server

**Option A: Free (Testing Only) - Use Your Computer**
- ⚠️ Your computer must stay on 24/7
- ⚠️ Need to expose your computer to internet (security risk)
- Use ngrok or similar tunnel service

**Option B: $5/month - Cloud VM (Recommended)**
- ✅ Always available
- ✅ More secure
- ✅ Better performance
- Providers: DigitalOcean, Linode, Vultr, Hetzner

### Step 2: Set Up Ollama Server

**If using a cloud VM:**

1. Create an Ubuntu 22.04 VM (2GB RAM minimum)

2. SSH into your VM:
   ```bash
   ssh user@your-vm-ip
   ```

3. Upload files:
   ```bash
   # From your local machine
   scp Modelfile setup-ollama-server.sh user@your-vm-ip:~/
   ```

4. Run setup script:
   ```bash
   # On the VM
   chmod +x setup-ollama-server.sh
   ./setup-ollama-server.sh
   ```

5. Configure firewall:
   ```bash
   sudo ufw allow 11434/tcp
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

### Step 3: Deploy to Streamlit Cloud

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Add Ollama integration"
   git push
   ```

2. **Go to** [share.streamlit.io](https://share.streamlit.io)

3. **Deploy your app:**
   - Click "New app"
   - Select your GitHub repo
   - Set main file: `app.py`

4. **Add secret in app settings:**
   ```toml
   OLLAMA_HOST = "http://YOUR-VM-IP:11434"
   ```
   Replace `YOUR-VM-IP` with your actual VM IP address

5. **Save and reboot the app**

### Step 4: Test It!

Visit your Streamlit Cloud URL. The app should now connect to your Ollama server!

## Security Notes

### For Production:
1. **Use HTTPS** - Set up Nginx with SSL (see [DEPLOYMENT.md](DEPLOYMENT.md))
2. **Use a domain name** - Instead of IP address
3. **Consider VPN** - Or IP whitelisting

### Quick Security Check:
```bash
# On your VM, check if Ollama is accessible
curl http://localhost:11434/api/tags

# From your computer, test external access
curl http://YOUR-VM-IP:11434/api/tags
```

Both should return JSON with your models list.

## Cost Breakdown

| Component | Cost | Required |
|-----------|------|----------|
| Streamlit Cloud | FREE | ✅ Yes |
| Cloud VM (2GB) | $5-6/mo | ✅ Yes |
| Domain name | $12/year | Optional |
| SSL Certificate | FREE | Recommended |
| **Total** | **$5-6/month** | |

## Troubleshooting

### Can't connect to Ollama
```bash
# Check if Ollama is running
systemctl status ollama

# Check firewall
sudo ufw status

# Test locally first
curl http://localhost:11434/api/tags
```

### Model not found
```bash
# List models
ollama list

# Recreate model
ollama create gearhead8b -f Modelfile
```

### Streamlit app shows error
- Check OLLAMA_HOST is set correctly in secrets
- Try accessing http://YOUR-VM-IP:11434/api/tags in browser
- Check VM firewall allows port 11434

## Need Help?

See detailed instructions in:
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide
- **[README.md](README.md)** - Application documentation

## Alternative Option: Skip Cloud Deployment

If you don't want to manage a server, you can:
1. Run everything locally (Ollama + Streamlit)
2. Use `streamlit run app.py` on your computer
3. Access at http://localhost:8502
4. No cloud deployment needed!

This works great for personal use or testing.
