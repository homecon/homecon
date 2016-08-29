# Unit tests
To run the unit tests for the homecon plugin several steps need to be taken.

Create a project folder and clone the HomeCon and Smarthome.py projects into this folder
```
mkdir somefolder
cd somefolder
git clone https://github.com/BrechtBa/smarthome.git
git clone https://github.com/BrechtBa/homecon.git
```

Create a virtual environment to hold the python dependencies
```
virtualenv -p python3 env
```

Activate the virtual environment with:
```
source env/bin/activate
```

Install python dependencies:
```
pip install ephem
pip install PyMySQL
```

Set up a mysql database. Somewhere on the way you'll be asked to enter a mysql root password 
```
sudo apt-get -y install mysql-server
```

Log in to mysql to create a database for testing. In the line below replace `yourmysqlrootpassword` with the mysql root password you enterd above but keep the `passwordusedfortesting`:
```
mysql -u root -pyourmysqlrootpassword
CREATE DATABASE IF NOT EXISTS homecon_test;
GRANT ALL PRIVILEGES ON homecon_test.* TO 'homecon_test'@'localhost' identified by 'passwordusedfortesting';
exit
```



Go to the tests folder
```
cd homecon/plugins/homecon/tests
```

To run all tests run
```
python all.py
```
