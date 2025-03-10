# Discord Proxy Launcher
### Discord Proxy Başlatıcı

Tags/Etiketler: `#discord-proxy` `#proxy-manager` `#goodbydpi` `#isp-bypass` `#ssl-proxy` `#python` `#network-tools` `#proxy-automation` `#türkçe` `#proxy-validator`

This project helps bypass ISP restrictions for Discord access by temporarily using SSL proxies in conjunction with GoodbyDPI. It automatically manages the proxy connection process during Discord launch and removes the proxy once the connection is established.

## Purpose

When GoodbyDPI alone is not sufficient to access Discord, this tool:
1. Temporarily enables a validated SSL proxy
2. Launches Discord and helps establish the initial connection
3. Automatically removes the proxy once Discord is successfully connected
4. Works alongside GoodbyDPI to bypass ISP restrictions effectively

## Features

- Automated proxy management for Discord launch
- Integration with GoodbyDPI
- Uses validated SSL proxies
- Automatic proxy removal after successful connection
- Easy to use Python-based launcher

## Prerequisites

- Python 3.x
- GoodbyDPI installed and running
- Required Python packages (requirements.txt)
- Working SSL proxies list (csv format)

## Installation

1. Make sure you have GoodbyDPI running
2. Clone this repository
3. Install required Python packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Ensure GoodbyDPI is running
2. Run the launcher:
```bash
python discord_proxy_launcher.py
```

## Proxy Source

The SSL proxies used in this project are validated using [SSL-Proxy-Validator](https://github.com/alp55/SSL-Proxy-Validator), another project that helps in finding and validating working SSL proxies.

## Author

- **Alperen Ulutaş**
- Email: alperen.ulutas.1@gmail.com
- GitHub: [@alp55](https://github.com/alp55)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.