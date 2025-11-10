import { useState, useEffect, useRef, useCallback } from 'react';

const useWebSocket = (url, options = {}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [reconnectCount, setReconnectCount] = useState(0);
  const [error, setError] = useState(null);
  
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);
  
  const {
    autoReconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    onOpen,
    onClose,
    onError,
    onMessage
  } = options;

  const connect = useCallback(() => {
    try {
      setError(null);
      ws.current = new WebSocket(url);
      
      ws.current.onopen = (event) => {
        setIsConnected(true);
        setReconnectCount(0);
        setError(null);
        if (onOpen) onOpen(event);
      };
      
      ws.current.onclose = (event) => {
        setIsConnected(false);
        if (onClose) onClose(event);
        
        // Reconnexion automatique
        if (autoReconnect && reconnectCount < maxReconnectAttempts) {
          reconnectTimeout.current = setTimeout(() => {
            setReconnectCount(prev => prev + 1);
            connect();
          }, reconnectInterval);
        }
      };
      
      ws.current.onerror = (event) => {
        setError('Erreur de connexion WebSocket');
        if (onError) onError(event);
      };
      
      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          if (onMessage) onMessage(data);
        } catch (err) {
          console.error('Erreur parsing message:', err);
        }
      };
      
    } catch (err) {
      setError('Erreur création WebSocket');
      console.error('Erreur:', err);
    }
  }, [
    url, 
    autoReconnect, 
    reconnectInterval, 
    maxReconnectAttempts, 
    reconnectCount,
    onOpen, 
    onClose, 
    onError, 
    onMessage
  ]);

  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }
    
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
    
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message) => {
    if (ws.current && isConnected) {
      try {
        const data = typeof message === 'string' ? message : JSON.stringify(message);
        ws.current.send(data);
        return true;
      } catch (err) {
        setError('Erreur envoi message');
        console.error('Erreur:', err);
        return false;
      }
    } else {
      setError('WebSocket non connecté');
      return false;
    }
  }, [isConnected]);

  const reconnect = useCallback(() => {
    disconnect();
    setReconnectCount(0);
    connect();
  }, [disconnect, connect]);

  // Nettoyage à la destruction
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  // Connexion initiale
  useEffect(() => {
    if (url) {
      connect();
    }
    
    return () => {
      disconnect();
    };
  }, [url, connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    error,
    reconnectCount,
    sendMessage,
    disconnect,
    reconnect
  };
};

export default useWebSocket;