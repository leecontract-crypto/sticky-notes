import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getAuth, onAuthStateChanged, signInWithPopup, signInWithRedirect, GoogleAuthProvider, signOut } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import { initializeFirestore, persistentLocalCache, collection, addDoc, doc, updateDoc, deleteDoc, onSnapshot, query, orderBy, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";
import { firebaseConfig } from "./firebase-config.js";

const $ = id => document.getElementById(id);
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});

// slide-out tab (remembers open/closed on this device)
const setOpen = o => {
  document.body.classList.toggle('open', o);
  $('tab').innerHTML = o ? '&#9654;' : '&#9664;';
  // The desktop launcher (float/float.py) reads the window title to resize the floating window.
  document.title = o ? 'Sticky Notes [open]' : 'Sticky Notes [closed]';
  try { localStorage.open = o ? 1 : 0; } catch {}
};
if (new URLSearchParams(location.search).has('float')) document.body.classList.add('float');
$('tab').onclick = () => setOpen(!document.body.classList.contains('open'));
try { setOpen(!document.body.classList.contains('float') && localStorage.open === '1'); } catch { setOpen(false); }

if (!firebaseConfig.apiKey) {
  $('signin').hidden = false; $('cfgmsg').hidden = false; $('signin-btn').hidden = true;
} else {
  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);
  const db = initializeFirestore(app, { localCache: persistentLocalCache() });
  let unsub = null, notesCol = null;

  $('signin-btn').onclick = async () => {
    const p = new GoogleAuthProvider();
    try { await signInWithPopup(auth, p); } catch { await signInWithRedirect(auth, p); }
  };
  $('signout').onclick = () => signOut(auth);

  onAuthStateChanged(auth, user => {
    if (unsub) { unsub(); unsub = null; }
    $('signin').hidden = !!user; $('app').hidden = !user;
    if (!user) return;
    notesCol = collection(db, 'users', user.uid, 'notes');
    unsub = onSnapshot(query(notesCol, orderBy('created', 'desc')),
      snap => render(snap.docs.map(d => ({ id: d.id, ...d.data() }))));
  });

  function render(notes) {
    $('notes').replaceChildren(...notes.filter(n => !n.paused).map(card));
    const p = notes.filter(n => n.paused);
    $('paused-h').hidden = !p.length;
    $('paused').replaceChildren(...p.map(card));
  }

  function card(n) {
    const el = document.createElement('div');
    el.className = 'note' + (n.paused ? ' paused' : '');
    const h = document.createElement('h4'); h.textContent = n.title || '(no title)';
    el.append(h);
    if (!n.paused) { const p = document.createElement('p'); p.textContent = n.body || ''; el.append(p); }
    const b = document.createElement('div'); b.className = 'btns';
    const pause = document.createElement('button');
    pause.textContent = n.paused ? '▶' : '⏸';
    pause.title = n.paused ? 'Reopen' : 'Pause';
    pause.onclick = () => updateDoc(doc(notesCol, n.id), { paused: !n.paused });
    const done = document.createElement('button');
    done.textContent = '✓'; done.title = 'Done (deletes)';
    done.onclick = () => deleteDoc(doc(notesCol, n.id));
    b.append(pause, done); el.append(b);
    return el;
  }

  $('add').onsubmit = e => {
    e.preventDefault();
    const title = $('new-title').value.trim(), body = $('new-body').value.trim();
    if (!title && !body) return;
    addDoc(notesCol, { title, body, paused: false, created: serverTimestamp() });
    $('new-title').value = ''; $('new-body').value = '';
  };

  // Dictation where the browser supports it; otherwise use the keyboard's mic button.
  // iOS's built-in speech API crashes in home-screen apps, so iPhones/iPads use the keyboard mic.
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const SR = isIOS ? null : (window.SpeechRecognition || window.webkitSpeechRecognition);
  if (!SR) {
    $('mic').title = "Use your keyboard's mic button to dictate";
    $('mic').onclick = () => $('new-body').focus();
  } else {
    const rec = new SR(); rec.lang = 'en-GB'; rec.interimResults = false;
    rec.onresult = ev => {
      const f = $('new-body');
      f.value = (f.value ? f.value + ' ' : '') + ev.results[0][0].transcript;
    };
    rec.onend = () => $('mic').classList.remove('on');
    $('mic').onclick = () => { try { rec.start(); $('mic').classList.add('on'); } catch { rec.stop(); } };
  }
}
