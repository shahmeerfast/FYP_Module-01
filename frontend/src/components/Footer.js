import React from 'react';

const Footer = () => {
  return (
    <footer className="mt-12">
      <div className="container mx-auto px-4 py-8 text-center text-sm text-gray-500">
        <div className="bg-white/70 glass rounded-xl p-4 card-shadow inline-block">
          <span>© {new Date().getFullYear()} Requirements Engineering System · Built with React & Tailwind CSS</span>
        </div>
      </div>
    </footer>
  );
};

export default Footer;










