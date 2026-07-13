import React from 'react';
import { createRoot } from 'react-dom/client';
import App from '../App';
import NavDemo from './NavDemo';
import './main.css';

const rootElement = document.getElementById('root');

if (rootElement) {
  const root = createRoot(rootElement);
  // Uncomment the line below to see the enhanced navigation demo
  // root.render(<NavDemo />);
  
  // Default app
  root.render(<App />);
} else {
  console.error('Root element not found!');
}