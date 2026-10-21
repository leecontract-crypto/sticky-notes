# Setup (one time, about 15 minutes)

## 1. Create the Firebase project (free)
1. Go to https://console.firebase.google.com and sign in with your Google account.
2. **Add project** -> name it `sticky-notes` -> turn Google Analytics off -> Create.
3. **Build -> Authentication -> Get started -> Google -> Enable** (pick your email as support email) -> Save.
4. **Build -> Firestore Database -> Create database** -> choose a London/Europe location -> **Production mode** -> Create.
5. In Firestore open the **Rules** tab, replace everything with the contents of `firestore.rules` from this folder, and click **Publish**.
6. **Project settings (cog) -> General -> Your apps -> the `</>` Web icon** -> nickname `web` -> Register app.
   Copy the four values (apiKey, authDomain, projectId, appId) into `firebase-config.js`.
   (These are not secrets; the rules above are what protect your notes.)

## 2. Put it on the web (GitHub Pages)
1. Create a GitHub repo `sticky-notes` (public) and push this folder to it.
2. Repo **Settings -> Pages -> Deploy from branch -> main / root**. Your address will be `https://<your-username>.github.io/sticky-notes/`.
3. In Firebase **Authentication -> Settings -> Authorized domains**, add `<your-username>.github.io`.

## 3. Use it
- **Laptop / work PC:** open the address in Edge or Chrome -> menu -> *Install app* (or *Apps -> Install this site as an app*).
- **iPhone:** open it in Safari -> Share -> *Add to Home Screen*. To dictate, tap the mic on the iPhone keyboard.

## Test locally first
In this folder run `python -m http.server 8000`, open http://localhost:8000
(`localhost` is already authorised by Firebase by default).
