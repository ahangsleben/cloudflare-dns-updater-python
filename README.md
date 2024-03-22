# cloudflare-dns-updater-python
Automatic Cloudflare A-Record Updater in Python

## How to use
1. Copy the `config.ini.template` to `config.ini`.
2. Fill out the `config.ini` file with your Cloudflare Zone ID, API Token, and the
   domain name to update. You can get your Zone ID from the "Overview" tab of your
   Cloudflare site dashboard on the right-hand side under the "API" section. You can get
   a new API Token from the same section by clicking "Get your API token" and using the
   "Create Token" button. You can limit the token to only "DNS Update" capabilities on
   the specific zone you're intending to keep updated.
3. Install application dependencies. If you use
  [pipenv](https://pipenv.pypa.io/en/latest/) you can install dependencies using
  `pipenv sync`. Otherwise you can install the dependencies with `pip install requests`.
4. Run the script. If you're using pipenv use `pipenv run python update_dns_record.py`
   otherwise `python update_dns_record.py`.
5. Schedule the script with `cron` or your tool of preference.

## What it does
1. Finds your public IP using the `https://ifconfig.me/ip` API.
2. Uses the Cloudflare API to get your domain's DNS record.
3. Checks the IP on your current record against your public IP.
4. If the IPs didn't match, it uses the Cloudflare API to update your domain's DNS
   record.
