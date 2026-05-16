import { useState, useEffect, useCallback, useRef } from 'react';

export const useNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  const lastNotifId = useRef(localStorage.getItem('vibrisse_last_notif_id') || "");
  
  const fetchNotifications = useCallback(async () => {
    try {
      const response = await fetch('/api/system/notifications');
      const data = await response.json();
      
      if (data.notifications && data.notifications.length > 0) {
        const latest = data.notifications[data.notifications.length - 1];
        console.log("👻 Checking Ghost Notifications...", latest.id, lastNotifId.current);
        
        // Si on a une nouvelle notification
        if (latest.id !== lastNotifId.current) {
          console.log("🔔 NEW GHOST NOTIFICATION!", latest);
          lastNotifId.current = latest.id;
          localStorage.setItem('vibrisse_last_notif_id', latest.id);
          
          // Jouer un son (Petit "Pop" discret)
          const audio = new Audio('https://assets.mixkit.co/active_storage/sfx/2358/2358-preview.mp3');
          audio.volume = 0.4;
          audio.play().catch(e => console.log("Audio play blocked by browser policy", e));
          
          setNotifications(data.notifications);
        }
      }
    } catch (err) {
      // Silently fail to avoid console noise
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 5000); // Polling toutes les 5s
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  const clearNotifications = async () => {
    try {
      await fetch('/api/system/notifications/clear', { method: 'POST' });
      setNotifications([]);
    } catch (err) {
      console.error("Failed to clear notifications", err);
    }
  };

  return { notifications, clearNotifications };
};
