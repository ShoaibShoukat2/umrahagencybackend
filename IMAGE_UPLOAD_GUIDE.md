# 📸 Package Images Upload Guide

## 🎯 Image Fields Updated in add_packages.py

Script ne ab yeh image fields add kar di hain:
- **featured_image**: Package ki main image
- **hotel_image**: Hotel ki image

---

## 📁 Required Images to Upload

Upload these images to your backend media folder:

### **Packages Folder:** `/media/packages/`
1. `ramadhan-awal-2025.jpg` - Ramadhan Awal package
2. `ramadhan-akhir-2025.jpg` - Ramadhan Akhir package
3. `december-package-2026.jpg` - Both December packages
4. `baitul-maqdis-9days.jpg` - Baitul Maqdis 9 days
5. `baitul-maqdis-umrah-15days.jpg` - Baitul Maqdis + Umrah 15 days

### **Hotels Folder:** `/media/hotels/`
1. `rayhaan-rotana-makkah.jpg` - Rayhaan by Rotana hotel
2. `azka-almaqam-makkah.jpg` - Azka Al-Maqam hotel
3. `dallah-taibah-madinah.jpg` - Dallah Taibah hotel
4. `grand-court-jerusalem.jpg` - Grand Court Jerusalem
5. `al-safwah-makkah.jpg` - Al Safwah Makkah

---

## 🚀 How to Upload Images

### **Method 1: cPanel File Manager**

1. **Login to cPanel**
2. **File Manager** → Navigate to:
   ```
   /home/tmfouzys/backend.tmfouzy.sg/media/
   ```
3. **Create folders** if they don't exist:
   - `packages/`
   - `hotels/`
4. **Upload images** to respective folders
5. Set permissions to **644** for images

---

### **Method 2: FTP Upload (FileZilla)**

1. Connect to FTP:
   - Host: `ftp.tmfouzy.sg`
   - Username: `tmfouzys`
   - Password: your cPanel password
2. Navigate to: `/backend.tmfouzy.sg/media/`
3. Upload images to:
   - `/backend.tmfouzy.sg/media/packages/`
   - `/backend.tmfouzy.sg/media/hotels/`

---

### **Method 3: SSH/Terminal Upload**

From your local machine:
```bash
# Using SCP
scp ramadhan-awal-2025.jpg tmfouzys@tmfouzy.sg:~/backend.tmfouzy.sg/media/packages/
scp rayhaan-rotana-makkah.jpg tmfouzys@tmfouzy.sg:~/backend.tmfouzy.sg/media/hotels/
```

---

## 📋 Image Specifications

**Recommended Image Sizes:**
- **Package Featured Images**: 1200x800px (landscape)
- **Hotel Images**: 1200x800px (landscape)
- **Format**: JPG or PNG
- **Max File Size**: 500KB - 1MB (compressed)

**Image Optimization:**
- Use tools like TinyPNG or ImageOptim
- Keep file size under 1MB
- Use descriptive filenames
- Maintain aspect ratio 3:2

---

## 🔧 After Uploading Images

### **Step 1: Verify Image Paths**

Check in browser:
```
https://backend.tmfouzy.sg/media/packages/ramadhan-awal-2025.jpg
https://backend.tmfouzy.sg/media/hotels/rayhaan-rotana-makkah.jpg
```

### **Step 2: Run the Script**

```bash
cd ~/backend.tmfouzy.sg
python add_packages.py
```

### **Step 3: Verify in Admin**

1. Go to: `https://backend.tmfouzy.sg/admin/api/package/`
2. Check that packages have images displayed

---

## 🎨 Alternative: Use URLs (Temporary)

Agar images abhi upload nahi kar sakte, toh script mein URLs use kar sakte ho:

```python
'featured_image': 'https://example.com/ramadhan-package.jpg',
'hotel_image': 'https://example.com/hotel-makkah.jpg',
```

But **recommended** hai ki proper media folder mein upload karo.

---

## 📂 Final Media Folder Structure

```
/media/
├── packages/
│   ├── ramadhan-awal-2025.jpg
│   ├── ramadhan-akhir-2025.jpg
│   ├── december-package-2026.jpg
│   ├── baitul-maqdis-9days.jpg
│   └── baitul-maqdis-umrah-15days.jpg
├── hotels/
│   ├── rayhaan-rotana-makkah.jpg
│   ├── azka-almaqam-makkah.jpg
│   ├── dallah-taibah-madinah.jpg
│   ├── grand-court-jerusalem.jpg
│   └── al-safwah-makkah.jpg
├── passports/
├── order_screenshots/
└── logo.jpeg
```

---

## ⚠️ Common Issues

### **Issue 1: Image not showing**
**Solution:**
- Check file path is correct
- Verify file permissions (644)
- Check MEDIA_URL in settings.py
- Clear browser cache

### **Issue 2: Permission denied**
**Solution:**
```bash
cd ~/backend.tmfouzy.sg/media
chmod 755 packages hotels
chmod 644 packages/* hotels/*
```

### **Issue 3: URL not accessible**
**Solution:**
- Check `.htaccess` in media folder
- Verify MEDIA_ROOT in settings.py
- Check Apache/Nginx configuration

---

## ✅ Checklist

Before running script:
- [ ] Create `/media/packages/` folder
- [ ] Create `/media/hotels/` folder
- [ ] Upload all package images
- [ ] Upload all hotel images
- [ ] Set correct permissions
- [ ] Test image URLs in browser
- [ ] Run `python add_packages.py`
- [ ] Verify in admin panel

---

**🎉 Ab script run karo with images!**
