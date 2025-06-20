import discord
import asyncio
from playwright.async_api import async_playwright

TOKEN = 'MTM4NTcwNDQwMzMzOTcxMDUxNA.GYC2L4.GjgEhiVYel6NYSe9Rs-K7e0xoq1kZtWm_Y80J0'
CHANNEL_ID = 1385703980801462305
OLX_URL = 'https://www.olx.pl/elektronika/telefony/smartfony-telefony-komorkowe/iphone/sopot/q-iphone/?search%5Bdist%5D=100&search%5Border%5D=created_at:desc&search%5Bfilter_float_price:from%5D=60&search%5Bfilter_enum_state%5D%5B0%5D=used&search%5Bfilter_enum_state%5D%5B1%5D=damaged&search%5Bfilter_enum_phonemodel%5D%5B0%5D=iphone-xr&search%5Bfilter_enum_phonemodel%5D%5B1%5D=iphone-xs-max&search%5Bfilter_enum_phonemodel%5D%5B2%5D=iphone-16&search%5Bfilter_enum_phonemodel%5D%5B3%5D=iphone-x&search%5Bfilter_enum_phonemodel%5D%5B4%5D=iphone-14-pro-max&search%5Bfilter_enum_phonemodel%5D%5B5%5D=iphone-14-pro&search%5Bfilter_enum_phonemodel%5D%5B6%5D=iphone-14-plus&search%5Bfilter_enum_phonemodel%5D%5B7%5D=iphone-15&search%5Bfilter_enum_phonemodel%5D%5B8%5D=iphone-16-pro-max&search%5Bfilter_enum_phonemodel%5D%5B9%5D=iphone-16pro&search%5Bfilter_enum_phonemodel%5D%5B10%5D=iphone-16-plus&search%5Bfilter_enum_phonemodel%5D%5B11%5D=iphone-13-pro-max&search%5Bfilter_enum_phonemodel%5D%5B12%5D=iphone-14&search%5Bfilter_enum_phonemodel%5D%5B13%5D=iphone-se&search%5Bfilter_enum_phonemodel%5D%5B14%5D=iphone-11-pro-max&search%5Bfilter_enum_phonemodel%5D%5B15%5D=iphone-11-pro&search%5Bfilter_enum_phonemodel%5D%5B16%5D=iphone-13-mini&search%5Bfilter_enum_phonemodel%5D%5B17%5D=iphone-13&search%5Bfilter_enum_phonemodel%5D%5B18%5D=iphone-12-pro-max&search%5Bfilter_enum_phonemodel%5D%5B19%5D=iphone-12-pro&search%5Bfilter_enum_phonemodel%5D%5B20%5D=iphone-xs&search%5Bfilter_enum_phonemodel%5D%5B21%5D=iphone-13-pro&search%5Bfilter_enum_phonemodel%5D%5B22%5D=iphone-15-pro-max&search%5Bfilter_enum_phonemodel%5D%5B23%5D=iphone-15-pro&search%5Bfilter_enum_phonemodel%5D%5B24%5D=iphone-15-plus&search%5Bfilter_enum_phonemodel%5D%5B25%5D=iphone-12&search%5Bfilter_enum_phonemodel%5D%5B26%5D=iphone-11&search%5Bfilter_enum_phonemodel%5D%5B27%5D=iphone-12-mini'

intents = discord.Intents.default()
client = discord.Client(intents=intents)
seen_ads = set()

async def fetch_olx_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(OLX_URL)
        await page.wait_for_selector("div.css-1tqlkj0", timeout=10000)

        ad = await page.query_selector("div.css-1tqlkj0")
        if not ad:
            await browser.close()
            return None

        title = await ad.query_selector_eval("h6", "el => el.textContent")
        link = await ad.query_selector_eval("a", "el => el.href")
        if link in seen_ads:
            await browser.close()
            return None
        seen_ads.add(link)

        await page.goto(link)
        await page.wait_for_selector("h3[data-testid='ad-price-container']", timeout=10000)

        price = await page.locator("h3[data-testid='ad-price-container']").text_content()
        location = await page.locator("p[data-testid='location-date']").text_content()
        seller_info = await page.locator("div.css-1wi2w6s").text_content()
        description = await page.locator("div[data-cy='ad_description']").text_content()

        await browser.close()
        return {
            "title": title.strip(),
            "link": link,
            "price": price.strip(),
            "location": location.strip().split('-')[0].strip(),
            "seller_info": seller_info.strip(),
            "description": description.strip()[:300]
        }

@client.event
async def on_ready():
    print(f"🤖 Bot uruchomiony jako {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    while True:
        try:
            data = await fetch_olx_data()
            if data:
                msg = (
                    f"📱 **{data['title']}**\n"
                    f"💰 Cena: {data['price']}\n"
                    f"📍 Lokalizacja: {data['location']}\n"
                    f"🧑 Sprzedający: {data['seller_info']}\n"
                    f"📄 Opis: {data['description']}...\n"
                    f"🔗 [Zobacz ogłoszenie]({data['link']})"
                )
                await channel.send(msg)
        except Exception as e:
            print("❌ Błąd:", e)
        await asyncio.sleep(60)

client.run(TOKEN)
