import { getApp, getApps, initializeApp } from 'firebase/app'
import { getAuth, GoogleAuthProvider, onAuthStateChanged, signInWithPopup, type User } from 'firebase/auth'

const config = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
}

export const firebaseEnabled = Object.values(config).every(Boolean)
export const firebaseAuth = firebaseEnabled ? getAuth(getApps().length ? getApp() : initializeApp(config)) : null

export function watchFirebaseUser(listener: (user: User | null) => void) {
  return firebaseAuth ? onAuthStateChanged(firebaseAuth, listener) : () => undefined
}

export async function signInWithGoogle() {
  if (!firebaseAuth) throw new Error('Firebase Auth is not configured')
  await signInWithPopup(firebaseAuth, new GoogleAuthProvider())
}

export async function getFirebaseToken() {
  return firebaseAuth?.currentUser ? firebaseAuth.currentUser.getIdToken() : null
}
