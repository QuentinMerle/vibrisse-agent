import React from 'react';
import './MessageSkeleton.css';

const MessageSkeleton = () => {
  return (
    <div className="skeleton-wrapper">
      <div className="skeleton-avatar"></div>
      <div className="skeleton-body">
        <div className="skeleton-line short"></div>
        <div className="skeleton-line long"></div>
        <div className="skeleton-line medium"></div>
      </div>
    </div>
  );
};

export default MessageSkeleton;
