import os
import time
import random
import logging
import pandas as pd
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
INPUT_FILE = "shiftai_leads.xlsx"
OUTPUT_FILE = "shiftai_leads_processed.xlsx"

# Determine API credentials and provider
KIE_API_KEY = os.getenv("KIE_API_KEY") or "c265863dc372ef4fe5b1d34c1732a128" # Default to user provided Kie key if not env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if KIE_API_KEY:
    logger.info("Using Kie.ai API gateway (Google DeepMind Gemini 2.5 Flash).")
    BASE_URL = "https://api.kie.ai/gemini-2.5-flash/v1"
    MODEL_NAME = "gemini-2.5-flash"
    API_KEY = KIE_API_KEY
else:
    logger.info("Using official OpenAI API gateway.")
    BASE_URL = None
    MODEL_NAME = "gpt-4o-mini"
    API_KEY = OPENAI_API_KEY

# System prompt for B2B outreach pivot (operational dispatch service МенеджAI)
SYSTEM_PROMPT = """You are a senior B2B growth architect and elite sales copywriter.
Your goal is to write a highly personalized, compelling, and natural-sounding cold message to owners/operators of cleaning companies or courier delivery services in Russia.
Avoid sounding like a bot. Do not use generic corporate jargon or overly aggressive sales pitches.
The tone should be peer-to-peer, respectful, helpful, and concise.
Write the output message in Russian, since the target audience consists of Russian business owners."""

def generate_prompt(brand_name, locations_count, website, contact_info, sphere):
    """
    Constructs a highly detailed prompt containing context and constraints for the LLM.
    """
    sphere_text = "клининга (уборка квартир и офисов)" if sphere == "cleaning" else "последней мили / курьерской доставки"
    
    return f"""Write a cold B2B outreach message based on the following lead context and product offering:

LEAD CONTEXT:
- Brand Name (Название компании): {brand_name}
- Number of Locations/Hubs (Количество филиалов/хабов): {locations_count}
- Website: {website}
- Industry Niche: {sphere_text}
- Contact: {contact_info}

PRODUCT CONTEXT (МенеджAI):
- What it is: An autonomous AI-dispatcher for cleaning companies and courier services.
- How it works: Imports employee database and schedule in 5 minutes (no POS system integration required). Automatically distributes orders based on geolocation, current load, and urgency. Co-ordinates shifts and tasks employees directly via Telegram.
- Pain points solved: High dispatcher workload/mistakes, courier/cleaner turnover, and labor cost (ФОТ) overruns.
- Primary Benefit: Cuts labor costs (ФОТ) by 20% and completely automates dispatcher routines.

OFFER:
- Exclusive test-drive for 9,900 RUB (instead of 25,000 RUB) for only 3 local chains/agencies.
- Risk reversal: 14-day money-back guarantee if labor costs do not decrease.

OUTREACH CONSTRAINTS:
1. Start directly by mentioning their brand name '{brand_name}' and their scale '{locations_count}' to make the message feel organic (e.g. "Приветствую! Видел, что у {brand_name} сейчас {locations_count} филиалов...").
2. Keep the message under 130 words.
3. Address the pain of manual dispatching, dispatcher mistakes, or employee turnover/standby costs.
4. Do not use em-dashes (—), placeholders, or brackets.
5. End with a clear, low-friction call to action (e.g. asking if they want to calculate potential savings or see a quick demo).
6. Write in natural Russian suitable for Telegram or WhatsApp.
"""

def get_personalized_message(client, prompt):
    """
    Calls the LLM API with retry logic and error handling.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"API call failed on attempt {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"Failed to generate message after {max_retries} attempts.")
                return None

def simulate_yandex_maps_scraping():
    """
    Simulates scraping Yandex Maps for B2B cleaning and courier leads.
    Filters out solo freelancers (e.g. 'Частный клинер Елена', 'ИП Иванов') 
    and giant monopolies (e.g. 'Яндекс Доставка', 'Вкусно и Точка'),
    focusing on local networks with 2 to 10 hubs/locations.
    """
    logger.info("Initializing Yandex Maps scraping simulation for cleaning/delivery services...")
    time.sleep(1.0)
    
    # Mock data that represents parsed leads satisfying the filters
    scraped_leads = [
        {
            "Brand Name": "Чистый Дом",
            "Number of locations": 4,
            "Website": "clean-house-spb.ru",
            "Contact": "+79119283746",
            "Sphere": "cleaning"
        },
        {
            "Brand Name": "КурьерЭкспресс",
            "Number of locations": 3,
            "Website": "courierexpress-msk.ru",
            "Contact": "@courier_express_dispatch",
            "Sphere": "delivery"
        },
        {
            "Brand Name": "КлинингПрофи",
            "Number of locations": 6,
            "Website": "cleaning-profi.ru",
            "Contact": "+79031234567",
            "Sphere": "cleaning"
        },
        {
            "Brand Name": "Быстрый Ровер",
            "Number of locations": 5,
            "Website": "fastrover-delivery.ru",
            "Contact": "+79998887766",
            "Sphere": "delivery"
        }
    ]
    
    logger.info(f"Scraped and filtered {len(scraped_leads)} leads from Yandex Maps successfully.")
    df = pd.DataFrame(scraped_leads)
    df.to_excel(INPUT_FILE, index=False)
    logger.info(f"Saved initial scraped leads to '{INPUT_FILE}'.")
    return df

def process_leads():
    """
    Main entry point for lead processing and B2B outreach generation.
    """
    if not API_KEY:
        logger.error("No API key provided. Set KIE_API_KEY or OPENAI_API_KEY environment variable.")
        print("\n[ERROR] Please set your API key environment variable:")
        print("export KIE_API_KEY='your-kie-api-key'\n")
        return

    # 1. Initialize client
    if BASE_URL:
        client = OpenAI(
            api_key=API_KEY, 
            base_url=BASE_URL,
            default_headers={"User-Agent": "Mozilla/5.0"}
        )
    else:
        client = OpenAI(api_key=API_KEY)

    # 2. Check for input file or run Yandex Maps scraper
    if not os.path.exists(INPUT_FILE):
        df = simulate_yandex_maps_scraping()
    else:
        try:
            df = pd.read_excel(INPUT_FILE)
            logger.info(f"Loaded {len(df)} leads from existing file '{INPUT_FILE}'.")
        except Exception as e:
            logger.error(f"Failed to read '{INPUT_FILE}': {e}")
            return

    # 3. Check for required columns
    required_cols = ["Brand Name", "Number of locations", "Website", "Contact", "Sphere"]
    for col in required_cols:
        if col not in df.columns:
            # If sphere is missing, default it to cleaning for backward compatibility
            if col == "Sphere":
                df["Sphere"] = "cleaning"
            else:
                logger.error(f"Missing required column: '{col}'. Present: {list(df.columns)}")
                return

    # Initialize output column if not exists
    if "Personalized Message" not in df.columns:
        df["Personalized Message"] = ""

    # 4. Generate outreach messages
    processed_count = 0
    for index, row in df.iterrows():
        # Skip if already processed
        if pd.notna(row["Personalized Message"]) and str(row["Personalized Message"]).strip() != "":
            continue

        brand_name = row["Brand Name"]
        locations = row["Number of locations"]
        website = row["Website"]
        contact = row["Contact"]
        sphere = row["Sphere"]

        logger.info(f"Processing B2B Lead {index + 1}/{len(df)}: {brand_name} ({locations} hubs)")

        prompt = generate_prompt(brand_name, locations, website, contact, sphere)
        message = get_personalized_message(client, prompt)

        if message:
            df.at[index, "Personalized Message"] = message
            processed_count += 1
            df.to_excel(OUTPUT_FILE, index=False)
            logger.info(f"Saved message for {brand_name}.")
            
            # Rate limit/smart delay
            time.sleep(random.uniform(1.0, 2.5))
        else:
            logger.warning(f"Could not generate message for {brand_name}.")

    logger.info(f"Outreach generation complete. Processed {processed_count} leads. Output saved to '{OUTPUT_FILE}'.")

    # 5. Output simulation display
    print("\n" + "="*50)
    print("SIMULATED TELEGRAM/WHATSAPP DISPATCH QUEUE:")
    print("="*50)
    for index, row in df.iterrows():
        msg = row.get("Personalized Message")
        if msg and pd.notna(msg):
            print(f"\n[QUEUE] Target: {row['Contact']} ({row['Brand Name']})")
            print(f"[PREVIEW]:\n{msg}")
            print(f"[STATUS] Simulating anti-spam interval...")
            print(f"[STATUS] Dispatched successfully.")
            print("-" * 30)

if __name__ == "__main__":
    process_leads()
