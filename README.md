## Custom Report

custom report

bench get-app https://github.com/matiyas-develop/Custom-Stock-Projected-Qty

bench --site [site.name] install-app custom_report

bench --site [site.name] migrate

sudo supervisorctl restart all


**For Update Custom App**

/frappe-bench/apps/custom_report$ git pull

/frappe-bench/apps/custom_report$ bench --site sitename migrate
  
/frappe-bench/apps/custom_report$ sudo supervisorctl restart all
  
  

#### License

MIT
