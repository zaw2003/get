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

            

            # -------------------------------------------------------------
            # [ဒီနေရာကစပြီး အဆင့်တစ်ဆင့် ထပ်တိုးလိုက်တာပါ]
            # -------------------------------------------------------------
            # ၁။ မိလာတဲ့ URL ထဲက /auth/wifidogAuth/login/? နေရာမှာ သင်လိုချင်တဲ့ API URL နဲ့ အစားထိုးလိုက်တယ်
            target_stage_url = portal_url.replace(
                "/auth/wifidogAuth/login/?", "/api/auth/wifidog?stage=portal&"
            )
            
            print("[*] ဒုတိယအဆင့် URL တစ်ခုလုံးကြီးကို ပြောင်းလဲတည်ဆောက်ပြီးပါပြီ -")
            print(f"-> Target URL: {target_stage_url}")
            
            # ၂။ သင်ပြပေးထားတဲ့ Header ပုံစံအတိုင်း ပြင်ဆင်တယ်
            next_headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 14; 22101316C Build/UP1A.231005.007) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.7827.91 Mobile Safari/537.36",
                "X-Requested-With": "mark.via.gp",
                "Referer": portal_url  # မူရင်း URL ကို Referer အဖြစ် ပြန်ထည့်ပေးထားပါတယ်
            }
            
            
            # ၃။ target_stage_url တစ်ခုလုံးကြီးဆီကို Request တိုက်ရိုက်ပို့ပြီး ယူလိုက်တာပါ
            async with session.get(target_stage_url, headers=next_headers, timeout=TIMEOUT_SEC) as r2:
                portal_response_text = await r2.text()
                
               
                
                # လိုချင်တဲ့ Response စာသား သို့မဟုတ် u Object ကို ပြန်ပေးလို့ရပါတယ်
                u = urlparse(target_stage_url)
                return portal_response_text  

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
