# Xiannong Campus Secondhand Market

This is a WeChat miniprogram for in-campus secondhand trading for students in China Agricultural University (CAU). This is a curriculum design project for CAU's software engineering course.  

Contributing: See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for contribution guidelines.

# Getting Started

To deploy this instance on your device, you'll need to complete the following steps: 

1. Download *WeiXin Dev Tools* first.
2. Use the *import project* method in WeiXin Dev Tools to open folder */miniprogram*. Now you can access the miniprogram front-end through the integrated simulator. 
3. Setup a Python environment to run the backend server. Suggested Python version is Python 3.12. Use pip to install packages listed in */server/requirements.txt*.
4. Go into */server* and run command `uvicorn app.main:app --reload --port 8000` in your console.
5. Install MySQL 8.0 server to serve as the back-end database.
6. Run the SQL script */server/app/db/schema.sql* to create the whole required database in your MySQL 8.0 server.
7. Configure */server/.env* according to your own MySQL 8.0 server settings. You might want to restart the Uvicorn server after you finish configuring this. 
8. Now the application should be up and running. 
