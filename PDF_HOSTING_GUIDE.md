# PDF Hosting Guide for Citations

To make citations clickable with links to the actual PDF files, you need to host your PDFs online and configure the base URL.

## Quick Setup

### Option 1: Use GitHub (Free, Simple)

1. **Create a public GitHub repository for your PDFs:**
   ```bash
   # Create a new repo on GitHub called "gearhead-pdfs"
   # Clone it locally
   git clone https://github.com/YOUR-USERNAME/gearhead-pdfs.git
   cd gearhead-pdfs
   ```

2. **Upload your PDFs:**
   ```bash
   # Copy your PDFs to the repo
   cp /path/to/your/pdfs/*.pdf ./

   # Commit and push
   git add .
   git commit -m "Add equipment manuals"
   git push
   ```

3. **Get the raw file URL:**
   - Go to any PDF in GitHub
   - Click "Raw" or "Download"
   - Copy the URL - it will look like:
     `https://raw.githubusercontent.com/YOUR-USERNAME/gearhead-pdfs/main/FILENAME.pdf`
   - The base URL is: `https://raw.githubusercontent.com/YOUR-USERNAME/gearhead-pdfs/main`

4. **Set the environment variable:**

   Add to your `.env` file:
   ```bash
   BASE_PDF_URL=https://raw.githubusercontent.com/YOUR-USERNAME/gearhead-pdfs/main
   ```

   Or for Streamlit Cloud, add to secrets:
   ```toml
   BASE_PDF_URL = "https://raw.githubusercontent.com/YOUR-USERNAME/gearhead-pdfs/main"
   ```

### Option 2: Use AWS S3 (Recommended for Production)

1. **Create an S3 bucket:**
   ```bash
   # Install AWS CLI
   pip install awscli

   # Configure AWS credentials
   aws configure

   # Create bucket
   aws s3 mb s3://gearhead-equipment-manuals
   ```

2. **Upload PDFs:**
   ```bash
   # Upload all PDFs
   aws s3 sync /path/to/pdfs s3://gearhead-equipment-manuals/
   ```

3. **Make bucket public (or use CloudFront):**
   ```bash
   # Set public read policy
   aws s3api put-bucket-policy --bucket gearhead-equipment-manuals --policy '{
     "Version": "2012-10-17",
     "Statement": [{
       "Sid": "PublicReadGetObject",
       "Effect": "Allow",
       "Principal": "*",
       "Action": "s3:GetObject",
       "Resource": "arn:aws:s3:::gearhead-equipment-manuals/*"
     }]
   }'
   ```

4. **Set the base URL:**
   ```bash
   BASE_PDF_URL=https://gearhead-equipment-manuals.s3.amazonaws.com
   ```

### Option 3: Use Google Cloud Storage

1. **Create a bucket:**
   ```bash
   gsutil mb gs://gearhead-equipment-manuals
   ```

2. **Upload PDFs:**
   ```bash
   gsutil -m cp /path/to/pdfs/*.pdf gs://gearhead-equipment-manuals/
   ```

3. **Make bucket public:**
   ```bash
   gsutil iam ch allUsers:objectViewer gs://gearhead-equipment-manuals
   ```

4. **Set the base URL:**
   ```bash
   BASE_PDF_URL=https://storage.googleapis.com/gearhead-equipment-manuals
   ```

### Option 4: Use Cloudflare R2 (Cheapest Cloud Option)

- No egress fees
- S3-compatible API
- Free tier: 10GB storage
- Base URL: `https://pub-XXXXX.r2.dev`

## Testing

After setting up, test that citations work:

```bash
# Test the citation URLs
source venv/bin/activate
python check_pinecone_data.py
```

You should see clickable markdown links like:
```
[194385AE-12.pdf, p.8](https://YOUR-BASE-URL/194385AE-12.pdf#page=8)
```

## Important Notes

### PDF Page Anchors

The `#page=N` anchor in PDF URLs works in:
- ✅ Modern browsers (Chrome, Firefox, Safari, Edge)
- ✅ PDF.js viewers
- ❌ Some mobile browsers (may require PDF viewer app)

### Security Considerations

**Public Access:**
- If PDFs contain proprietary/confidential information, don't make them publicly accessible
- Use signed URLs or authentication instead

**Private Access with Signed URLs:**

For S3, you can generate temporary signed URLs:
```python
import boto3
from botocore.client import Config

s3 = boto3.client('s3', config=Config(signature_version='s3v4'))

def get_signed_url(filename, expiration=3600):
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': 'gearhead-equipment-manuals', 'Key': filename},
        ExpiresIn=expiration
    )
    return url
```

## Alternative: Local PDF Viewer

If you don't want to host PDFs online, you can:

1. Keep PDFs locally
2. Modify citations to show just the reference
3. Users can download PDFs separately

In this case, set no BASE_PDF_URL and citations will display as plain text.

## Cost Estimates

| Service | Free Tier | Cost After |
|---------|-----------|------------|
| GitHub | Unlimited for public repos | Free |
| AWS S3 | 5GB for 12 months | ~$0.023/GB/month |
| Google Cloud Storage | 5GB always free | ~$0.020/GB/month |
| Cloudflare R2 | 10GB always free | $0.015/GB/month |

## Next Steps

1. Choose a hosting option
2. Upload your PDFs
3. Set `BASE_PDF_URL` environment variable
4. Restart your Streamlit app
5. Citations will now be clickable links!
