import apiClient from '../api/client';

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = atob(base64);
  return Uint8Array.from([...rawData].map((char) => char.charCodeAt(0)));
}

export async function subscribeToPush() {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) return false;

  try {
    const reg = await navigator.serviceWorker.ready;

    const existing = await reg.pushManager.getSubscription();
    if (existing) return true;

    const res = await apiClient.get('/auth/push/vapid-key/');
    const vapidKey = res.data.public_key;
    if (!vapidKey) return false;

    const permission = await Notification.requestPermission();
    if (permission !== 'granted') return false;

    const subscription = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidKey),
    });

    await apiClient.post('/auth/push/subscribe/', {
      subscription: subscription.toJSON(),
    });

    return true;
  } catch (e) {
    console.error('Push subscription failed:', e);
    return false;
  }
}
