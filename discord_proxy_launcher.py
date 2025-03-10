import winreg
import subprocess
import time
import os
import psutil
import csv
import sys
import requests
import socket

def read_proxies_from_url():
    try:
        # Lokal ssl_working_proxies.csv dosyasından oku
        proxy_file = os.path.join(os.path.dirname(__file__), "ssl_working_proxies.csv")
        if not os.path.exists(proxy_file):
            raise Exception(f"Proxy dosyası bulunamadı: {proxy_file}")
            
        proxies = []
        with open(proxy_file, 'r') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                if row['ip'] and row['port']:
                    proxies.append((row['ip'], row['port']))
        
        if not proxies:
            raise Exception("Proxy listesi boş")
            
        print(f"Lokal proxy dosyasından {len(proxies)} proxy okundu")
        return proxies
        
    except Exception as e:
        print(f"Proxy listesi okuma hatası: {str(e)}")
        sys.exit(1)

def safe_set_proxy(proxy_host, proxy_port):
    """Proxy'i güvenli bir şekilde test edip ayarlar."""
    proxy_str = f"{proxy_host}:{proxy_port}"
    
    # Önce proxy'i test et
    try:
        session = requests.Session()
        session.trust_env = False
        session.verify = False
        
        proxies = {
            'http': f'http://{proxy_host}:{proxy_port}',
            'https': f'http://{proxy_host}:{proxy_port}'
        }
        
        # Kısa timeout süresiyle test et
        response = requests.head(
            'https://discord.com',
            proxies=proxies,
            timeout=(10, 10),  # Daha kısa timeout
            verify=True
        )
        
        if response.status_code == 200:
            print(f"Proxy test başarılı: {proxy_str}")
            return True
        
        print(f"Proxy test başarısız - Status code: {response.status_code}")
        return False
        
    except Exception as e:
        print(f"Proxy test hatası: {proxy_str} - {str(e)}")
        return False

def try_next_proxy(proxies, current_index=0):
    while current_index < len(proxies):
        proxy_host, proxy_port = proxies[current_index]
        print(f"Deneniyor proxy: {proxy_host}:{proxy_port}")
        
        # Önce güvenli proxy testini yap
        if not safe_set_proxy(proxy_host, proxy_port):
            print("Proxy testi başarısız, sıradaki deneniyor...")
            current_index += 1
            continue
            
        # Test başarılı olduysa proxy'i etkinleştir
        if not set_proxy(proxy_host, proxy_port, True):
            print("Proxy etkinleştirilemedi, sıradaki deneniyor...")
            current_index += 1
            continue
            
        # Sistem proxy ayarlarını kontrol et
        proxy_enabled, proxy_server = verify_system_proxy()
        if not proxy_enabled or f"{proxy_host}:{proxy_port}" not in proxy_server:
            print("Sistem proxy ayarları doğru değil, sıradaki deneniyor...")
            set_proxy(proxy_host, proxy_port, False)
            current_index += 1
            continue
            
        # Proxy bağlantısını tekrar test et
        if not verify_proxy_connection(proxy_host, proxy_port):
            print("Proxy bağlantı testi başarısız, sıradaki deneniyor...")
            set_proxy(proxy_host, proxy_port, False)
            current_index += 1
            continue
            
        return proxy_host, proxy_port, True
        
    return None, None, False

def set_proxy(host, port, enable=True):
    try:
        INTERNET_SETTINGS = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
            0, winreg.KEY_ALL_ACCESS)
        
        winreg.SetValueEx(INTERNET_SETTINGS, 'ProxyEnable', 0, winreg.REG_DWORD, 1 if enable else 0)
        if enable:
            proxy_string = f"{host}:{port}"
            winreg.SetValueEx(INTERNET_SETTINGS, 'ProxyServer', 0, winreg.REG_SZ, proxy_string)
            print(f"Proxy ayarlandı: {proxy_string}")
        
        INTERNET_SETTINGS.Close()
        return True
    except Exception as e:
        print(f"Proxy ayarlama hatası: {str(e)}")
        return False

def verify_proxy_connection(host, port):
    try:
        # Proxy ayarları
        proxies = {
            'http': f'http://{host}:{port}',
            'https': f'http://{host}:{port}'
        }
        
        # Discord.com'a bağlantıyı test et
        response = requests.get('https://discord.com', proxies=proxies, timeout=10)
        if response.status_code == 200:
            print("Discord.com'a proxy üzerinden başarıyla bağlanıldı")
            return True
        else:
            print(f"Discord.com bağlantı hatası: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Proxy bağlantı testi hatası: {str(e)}")
        return False

def verify_system_proxy():
    try:
        INTERNET_SETTINGS = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
            0, winreg.KEY_READ)
        
        proxy_enable = winreg.QueryValueEx(INTERNET_SETTINGS, 'ProxyEnable')[0]
        proxy_server = winreg.QueryValueEx(INTERNET_SETTINGS, 'ProxyServer')[0]
        
        INTERNET_SETTINGS.Close()
        return proxy_enable == 1, proxy_server
    except Exception as e:
        print(f"Sistem proxy kontrolü hatası: {str(e)}")
        return False, None

def is_discord_running():
    try:
        for proc in psutil.process_iter(['name']):
            if 'Discord.exe' in proc.info['name']:
                print(f"Discord process bulundu: {proc.info['name']}")
                return True
        return False
    except Exception as e:
        print(f"Process kontrol hatası: {str(e)}")
        return False

def main():
    try:
        # Discord path kontrolü
        discord_path = os.path.expandvars(r"%LOCALAPPDATA%\Discord\Update.exe")
        if not os.path.exists(discord_path):
            print(f"Discord bulunamadı: {discord_path}")
            sys.exit(1)
        print(f"Discord path doğrulandı: {discord_path}")

        # Proxy ayarlarını URL'den al
        proxies = read_proxies_from_url()
        print(f"Proxy listesi indirildi, toplam {len(proxies)} proxy bulundu")
        
        # Proxy'i etkinleştir ve doğrula
        proxy_host, proxy_port, success = try_next_proxy(proxies)
        if not success:
            print("Hiçbir proxy etkinleştirilemedi, çıkılıyor...")
            sys.exit(1)
        print(f"Proxy başarıyla etkinleştirildi: {proxy_host}:{proxy_port}")
        
        # Discord'u başlat
        print(f"Discord başlatılıyor: {discord_path}")
        try:
            process = subprocess.Popen([discord_path, "--processStart", "Discord.exe"], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
            print("Discord başlatma komutu çalıştırıldı")
        except Exception as e:
            print(f"Discord başlatma hatası: {str(e)}")
            set_proxy(proxy_host, proxy_port, False)
            sys.exit(1)
        
        # Discord'un başlamasını bekle
        timeout = 30  # 30 saniye timeout
        start_time = time.time()
        while not is_discord_running():
            if time.time() - start_time > timeout:
                print("Discord başlatılamadı - timeout")
                set_proxy(proxy_host, proxy_port, False)
                sys.exit(1)
            print("Discord başlaması bekleniyor...")
            time.sleep(2)
        
        print("Discord başarıyla başlatıldı")
        # Discord başladıktan sonra biraz bekle
        time.sleep(20)
        
        # Proxy'i devre dışı bırak
        if not set_proxy(proxy_host, proxy_port, False):
            print("Proxy devre dışı bırakılamadı!")
            sys.exit(1)
        print("Proxy başarıyla devre dışı bırakıldı")

    except Exception as e:
        print(f"Beklenmeyen hata: {str(e)}")
        try:
            set_proxy(proxy_host, proxy_port, False)
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
