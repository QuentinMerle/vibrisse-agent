import React from 'react';
import './VibrisseAvatar.css';

/**
 * VibrisseAvatar - Version SVG Officielle
 * Utilise le tracé exact fourni par l'utilisateur.
 */
export default function VibrisseAvatar({ size = 24, containerSize, isThinking = false, variant = 'default' }) {
  // Le ratio 1.6 est conservé pour le carré violet
  const finalContainerSize = containerSize || (size * 1.5);
  
  return (
    <div 
      className={`vibrisse-avatar-container ${isThinking ? 'thinking' : ''} ${variant}`}
      style={{ 
        width: `${finalContainerSize}px`, 
        height: `${finalContainerSize}px`
      }}
    >
      <svg 
        width={size} 
        height={(size * 33) / 48} /* Respecte le ratio 48x33 */
        viewBox="0 0 48 33" 
        version="1.1" 
        xmlns="http://www.w3.org/2000/svg" 
        xmlnsXlink="http://www.w3.org/1999/xlink" 
        style={{ fillRule: 'evenodd', clipRule: 'evenodd', strokeLinejoin: 'round', strokeMiterlimit: 2 }}
        className="vibrisse-svg-official"
      >
        <g transform="matrix(1,0,0,1,0,-1396.05)">
          <g id="Vibrisse-AI" transform="matrix(0.0111025,0,0,0.00780979,3.46222,1399.36)">
            <rect x="-311.842" y="-424.276" width="4247.28" height="4104.68" style={{ fill: 'none' }} />
            <g id="Merge" transform="matrix(22.0404,0,0,25.7451,-37290,-35766.3)">
              <g transform="matrix(4.1382,0,0,4.98326,-338.902,-5584.3)">
                <path 
                  d="M496.096,1418.48l-8.052,-2.63c-0.54,-0.176 -0.837,-0.763 -0.663,-1.309c0.175,-0.546 0.755,-0.846 1.295,-0.669l7.42,2.423l-0,-4.433c-0,-2.178 1.131,-4.09 2.832,-5.169c-0.002,-0.078 0.006,-0.157 0.022,-0.235l1.936,-9.131l0.163,-0.438l0.276,-0.363l0.368,-0.267l0.438,-0.152l0.462,-0.014l0.438,0.119l0.385,0.242l0.305,0.352l5.695,8.956l2.545,0l5.695,-8.956l0.305,-0.352l0.385,-0.242l0.438,-0.119l0.463,0.014l0.438,0.152l0.368,0.267l0.276,0.363l0.163,0.438l1.935,9.131c0.016,0.077 0.024,0.155 0.023,0.232c1.703,1.078 2.836,2.992 2.836,5.172l0,4.358l7.192,-2.348c0.54,-0.177 1.12,0.123 1.295,0.669c0.175,0.546 -0.122,1.133 -0.663,1.309l-7.824,2.555l0,1.079l7.824,2.555c0.541,0.177 0.838,0.763 0.663,1.309c-0.175,0.546 -0.755,0.846 -1.295,0.67l-7.192,-2.348l0,0.312c0,3.367 -2.704,6.1 -6.035,6.1l-17.12,0c-3.331,0 -6.035,-2.733 -6.035,-6.1l-0,-0.387l-7.42,2.423c-0.54,0.176 -1.12,-0.124 -1.295,-0.67c-0.174,-0.546 0.123,-1.132 0.663,-1.309l8.052,-2.629l-0,-0.93Zm27.133,-6.618c0,-2.219 -1.782,-4.021 -3.978,-4.021l-17.12,0c-2.195,0 -3.978,1.802 -3.978,4.021l0,10.12c0,2.219 1.783,4.021 3.978,4.021l17.12,-0c2.196,-0 3.978,-1.802 3.978,-4.021l0,-10.12Zm-4.496,-12.904l-4.246,6.678l5.662,0l-1.416,-6.678Zm-16.089,-0l-1.415,6.678l5.662,0l-4.247,-6.678Z" 
                  style={{ fill: 'white' }} 
                />
              </g>
              <g transform="matrix(4.32295,0,0,5.2612,-430.894,-5977.1)">
                <ellipse cx="505.31" cy="1416.49" rx="1.637" ry="3.124" style={{ fill: 'white' }} />
              </g>
              <g transform="matrix(4.32295,0,0,5.2612,-389.499,-5977.1)">
                <ellipse cx="505.31" cy="1416.49" rx="1.637" ry="3.124" style={{ fill: 'white' }} />
              </g>
            </g>
          </g>
        </g>
      </svg>
    </div>
  );
}
