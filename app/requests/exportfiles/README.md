When data is exported files are created on the server.
These file will be written to this folder so it is important to set the owner of this folder to www-data using:

```
sudo chown www-data:www-data homecon/www/requests/exportfiles
```