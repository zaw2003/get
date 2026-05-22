import asyncio
import re
from urllib.parse import urlparse
import aiohttp

# လိုအပ်တဲ့ Global variable တွေနဲ့ Constant တွေကို သတ်မှတ်ပေးထားတာပါ
CURRENT_SID = None
TIMEOUT_SEC = 10  # Timeout စက္ကန့်


async def get_sid_from_gateway(session):
    global CURRENT_SID
    trigger_url = "http://connectivitycheck.gstatic.com/generate_204"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        # allow_redirects=False ဖြစ်လို့ Captive Portal ဆီ Redirect မဖြစ်ဘဲ URL ကို ဖမ်းမိမှာပါ
        async with session.get(
            trigger_url, headers=headers, timeout=TIMEOUT_SEC, allow_redirects=False
        ) as r1:
            portal_url = None
            text = await r1.text()

            # နည်းလမ်း (၁) - Response Text ထဲမှာ <NextURL> ပါလား ရှာတာ
            xml_match = re.search(r"<NextURL>(.*?)</NextURL>", text)
            if xml_match:
                portal_url = xml_match.group(1).replace("&amp;", "&").strip()

            # နည်းလမ်း (၂) - HTTP Header ထဲက Location (Redirect URL) ကို ယူတာ
            elif "Location" in r1.headers:
                portal_url = r1.headers["Location"]

            # URL ရှာမတွေ့ရင် ဘာမှမလုပ်ဘဲ ပြန်လှည့်မယ်
            if not portal_url:
                print("[-] Portal URL ကို ရှာမတွေ့ပါ...")
                return None

            # --- ဒီနေရာမှာ u Object ကို တည်ဆောက်ပြီး တစ်ခုလုံးကို Print ထုတ်ပြတာပါ ---
            u = urlparse(portal_url)

            print("\n==============================================")
            print("[+] Portal URL တစ်ခုလုံးကို အောင်မြင်စွာ ဖမ်းမိပါပြီ!")
            print(f"-> Full URL: {portal_url}")
            
            print("==============================================\n")

            return u

    except Exception as e:
        print(f"[-] အမှားအယွင်းတစ်ခု ရှိခဲ့ပါတယ်: {e}")
        return None


# --- Script တစ်ခုလုံးကို စမ်းသပ်မောင်းနှင်မယ့် နေရာ (Main Run) ---
async def main():
    # ClientSession တစ်ခု ဆောက်ပြီး စမ်းသပ်တာပါ
    async with aiohttp.ClientSession() as session:
        result = await get_sid_from_gateway(session)
        if result:
            print("[*] အောင်မြင်စွာ လုပ်ဆောင်ပြီးစီးပါပြီ။")
        else:
            print("[!] Gateway ကနေ ဘာ URL မှ ပြန်မရခဲ့ပါ။")


# Asyncio နဲ့ Script တစ်ခုလုံးကို စတင်ပတ်မောင်းတာပါ
if __name__ == "__main__":
    asyncio.run(main())
