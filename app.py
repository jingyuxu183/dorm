from backend import app

# 这个文件仅用于Vercel部署
# Vercel会优先使用此文件作为入口点

# 直接导出app对象供Vercel使用
application = app 