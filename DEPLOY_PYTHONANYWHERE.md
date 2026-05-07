# 🚀 PythonAnywhere Deployment Guide

## 📋 Prerequisites
- PythonAnywhere account (Free tier is fine)
- Your project files ready
- API keys for Sarvam AI and Pinecone
- MongoDB database (we'll use MongoDB Atlas for cloud)

---

## 🔧 Step 1: Set Up MongoDB Atlas (Cloud Database)

Since PythonAnywhere doesn't have local MongoDB, we'll use MongoDB Atlas:

1. **Create MongoDB Atlas Account**
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Sign up for free tier

2. **Create Cluster**
   - Click "Build a Database"
   - Choose "M0 Sandbox" (Free)
   - Select a cloud provider and region closest to you

3. **Configure Network Access**
   - Go to "Network Access" → "Add IP Address"
   - Click "Allow Access from Anywhere" (0.0.0.0/0)

4. **Create Database User**
   - Go to "Database Access" → "Add New Database User"
   - Username: `collegechatbot`
   - Password: Generate a strong password
   - Give read/write permissions

5. **Get Connection String**
   - Go to "Database" → "Connect" → "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your actual password

---

## 🌐 Step 2: PythonAnywhere Setup

### 2.1 Create Account and Web App

1. **Sign Up**: [PythonAnywhere](https://www.pythonanywhere.com/)
2. **Create Web App**:
   - Dashboard → Web → "+ Add a new web app"
   - Framework: **Flask**
   - Python version: **Python 3.8+**
   - Project name: `college-chatbot`

### 2.2 Upload Your Files

1. **Go to Files** → Upload a file
2. **Upload these files**:
   ```
   app.py
   retriever.py
   document_processor.py
   auth_db_fixed.py
   pythonanywhere_wsgi.py
   requirements_pythonanywhere.txt
   .env
   templates/ (entire folder)
   ```

3. **Create directories**:
   - Create `uploads/` folder
   - Create `pdfs/` folder (optional)

### 2.3 Install Dependencies

1. **Open Bash Console**:
   - Dashboard → Consoles → "$ Bash"
   - Run these commands:

```bash
# Navigate to your project
cd College-Chatbot

# Install dependencies
pip install -r requirements_pythonanywhere.txt

# Verify installation
pip list
```

---

## ⚙️ Step 3: Configure Environment Variables

### 3.1 Create .env File

1. **In Bash console**, create .env file:
```bash
nano .env
```

2. **Add your configuration**:
```env
# AI Services
SARVAM_API_KEY=your_sarvam_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here

# Database (use your MongoDB Atlas connection string)
MONGODB_URI=mongodb+srv://collegechatbot:your_password@cluster0.xxxxx.mongodb.net/college-chatbot?retryWrites=true&w=majority

# Flask Configuration
SECRET_KEY=your_secret_key_here_generate_a_long_random_string
FLASK_ENV=production
```

3. **Save and exit** (Ctrl+X, Y, Enter)

---

## 🔧 Step 4: Configure Web Application

### 4.1 Update WSGI File

1. **Edit the WSGI file**:
   - Go to Web → your web app → "WSGI configuration file"
   - Click the link to edit
   - **IMPORTANT**: Replace `yourusername` with your actual PythonAnywhere username

2. **Update this line**:
```python
project_home = '/home/your_actual_username/College-Chatbot'
```

### 4.2 Configure Web App Settings

1. **Go to Web → your web app**
2. **Set these values**:
   - **Source code**: `/home/yourusername/College-Chatbot`
   - **Working directory**: `/home/yourusername/College-Chatbot`
   - **WSGI configuration file**: `/home/yourusername/College-Chatbot/pythonanywhere_wsgi.py`

---

## 🎯 Step 5: Test and Deploy

### 5.1 Test in Console

1. **In Bash console**, test your app:
```bash
cd /home/yourusername/College-Chatbot
python -c "from app import app; print('✅ App imports successfully')"
```

### 5.2 Reload Web App

1. **Go to Web → your web app**
2. **Click the big "Reload" button**
3. **Check for errors** in the error log

### 5.3 Access Your App

Your app will be live at:
```
http://yourusername.pythonanywhere.com
```

---

## 🔍 Step 6: Troubleshooting

### Common Issues and Solutions:

#### 1. Module Import Errors
```bash
# In Bash console, reinstall missing modules
pip install module_name
```

#### 2. Database Connection Issues
- Check your MongoDB Atlas connection string
- Ensure IP access is configured (0.0.0.0/0)
- Verify username and password

#### 3. File Upload Issues
- Create the uploads folder:
```bash
mkdir -p /home/yourusername/College-Chatbot/uploads
```

#### 4. Static Files Not Loading
- Check template paths
- Ensure static folder exists

#### 5. 504 Gateway Timeout
- Free accounts have limitations
- Optimize your code for faster execution
- Consider upgrading to paid plan for production

---

## 📊 Step 7: Monitor and Maintain

### Check Logs Regularly:
1. **Web App Logs**: Web → your web app → "Logs"
2. **Error Logs**: Look for any errors in the log files
3. **Server Logs**: Check for server-related issues

### Update Your App:
1. **Upload new files** to replace old ones
2. **Install new dependencies** if needed
3. **Reload the web app** after changes

---

## 🔒 Security Considerations

### Important Security Notes:

1. **API Keys**: Never commit API keys to Git
2. **Database**: Use strong passwords for MongoDB
3. **File Uploads**: Validate file types and sizes
4. **HTTPS**: Your app automatically gets HTTPS on PythonAnywhere
5. **Secret Key**: Use a long, random secret key

---

## 📈 Scaling Up

### When to Upgrade from Free Tier:

- **More CPU time**: Paid plans give more CPU
- **Custom domains**: Paid plans allow custom domains
- **More storage**: For file uploads and database
- **Better performance**: Faster response times

### Upgrade Options:
- **Hacker**: $5/month - Good for personal projects
- **Web Dev**: $12/month - Better performance
- **Custom**: For production applications

---

## 🎉 Success Checklist

Your deployment is successful when:

- ✅ App loads at your PythonAnywhere URL
- ✅ User registration works
- ✅ Login/logout functions
- ✅ File uploads work
- ✅ Chatbot responds to questions
- ✅ Document processing works
- ✅ No major errors in logs

---

## 🆘 Get Help

If you need help:

1. **PythonAnywhere Forums**: Active community support
2. **MongoDB Atlas Documentation**: For database issues
3. **Flask Documentation**: For web app issues
4. **GitHub Issues**: For project-specific problems

---

## 🌟 Next Steps

After successful deployment:

1. **Test all features** thoroughly
2. **Share with friends** and get feedback
3. **Monitor performance** and usage
4. **Consider custom domain** for professional look
5. **Add more features** based on user feedback

---

**🎊 Congratulations! Your Kongu Engineering College AI Chatbot is now live on the internet!**
