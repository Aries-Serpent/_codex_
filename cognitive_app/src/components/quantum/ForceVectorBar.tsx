import { motion } from 'framer-motion';

interface ForceVector {
  name: string;
  magnitude: number;
  direction: number;
  color: string;
}

interface ForceVectorBarProps {
  vector: ForceVector;
  index: number;
  maxMagnitude?: number;
}

export function ForceVectorBar({ vector, index, maxMagnitude = 100 }: ForceVectorBarProps) {
  const percentage = (vector.magnitude / maxMagnitude) * 100;
  
  const getDirectionLabel = (degrees: number) => {
    const normalized = ((degrees % 360) + 360) % 360;
    if (normalized >= 337.5 || normalized < 22.5) return 'E';
    if (normalized >= 22.5 && normalized < 67.5) return 'NE';
    if (normalized >= 67.5 && normalized < 112.5) return 'N';
    if (normalized >= 112.5 && normalized < 157.5) return 'NW';
    if (normalized >= 157.5 && normalized < 202.5) return 'W';
    if (normalized >= 202.5 && normalized < 247.5) return 'SW';
    if (normalized >= 247.5 && normalized < 292.5) return 'S';
    return 'SE';
  };

  const getMagnitudeLabel = (mag: number) => {
    if (mag >= 80) return 'Critical';
    if (mag >= 60) return 'High';
    if (mag >= 40) return 'Medium';
    if (mag >= 20) return 'Low';
    return 'Minimal';
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className="space-y-2"
    >
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: vector.color }}
          />
          <span className="font-medium text-foreground">{vector.name}</span>
        </div>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="font-mono">
            {vector.magnitude.toFixed(1)} N
          </span>
          <span className="flex items-center gap-1">
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              className="inline-block"
            >
              <motion.line
                x1="8"
                y1="8"
                x2={8 + 6 * Math.cos((vector.direction * Math.PI) / 180)}
                y2={8 - 6 * Math.sin((vector.direction * Math.PI) / 180)}
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              />
              <motion.polygon
                points={`
                  ${8 + 6 * Math.cos((vector.direction * Math.PI) / 180)},
                  ${8 - 6 * Math.sin((vector.direction * Math.PI) / 180)}
                  ${8 + 4 * Math.cos(((vector.direction + 150) * Math.PI) / 180)},
                  ${8 - 4 * Math.sin(((vector.direction + 150) * Math.PI) / 180)}
                  ${8 + 4 * Math.cos(((vector.direction - 150) * Math.PI) / 180)},
                  ${8 - 4 * Math.sin(((vector.direction - 150) * Math.PI) / 180)}
                `}
                fill="currentColor"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.3, delay: index * 0.1 + 0.5 }}
              />
            </svg>
            {getDirectionLabel(vector.direction)}
          </span>
        </div>
      </div>

      <div className="relative h-2 bg-muted rounded-full overflow-hidden">
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{
            backgroundColor: vector.color,
            boxShadow: `0 0 8px ${vector.color}40`,
          }}
          initial={{ width: '0%' }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: 'easeOut', delay: index * 0.1 }}
        />
        
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full opacity-50"
          style={{
            background: `linear-gradient(90deg, transparent, ${vector.color})`,
            width: '30%',
          }}
          animate={{
            x: ['-100%', '100%'],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
      </div>

      <div className="flex items-center justify-between text-xs">
        <span className="text-muted-foreground">
          {getMagnitudeLabel(vector.magnitude)}
        </span>
        <span className="font-mono text-muted-foreground">
          {vector.direction.toFixed(0)}°
        </span>
      </div>
    </motion.div>
  );
}
