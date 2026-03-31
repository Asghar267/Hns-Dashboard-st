import React from 'react';

interface CardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  description?: string;
}

const Card: React.FC<CardProps> = ({ title, value, icon, description }) => {
  return (
    <div className="bg-surface p-6 rounded-lg shadow-card transition-shadow hover:shadow-card-hover">
      <div className="flex justify-between items-start">
        <div className="flex flex-col">
          <h3 className="text-sm font-medium text-textSecondary uppercase">{title}</h3>
          <span className="text-3xl font-bold text-textPrimary mt-2">{value}</span>
        </div>
        <div className="p-3 bg-primary/10 text-primary rounded-lg">
          {icon}
        </div>
      </div>
      {description && <p className="text-xs text-textSecondary mt-4">{description}</p>}
    </div>
  );
};

export default Card;
