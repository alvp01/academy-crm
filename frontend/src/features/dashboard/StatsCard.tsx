import { ReactNode } from "react";
import { Card } from "../../components/ui/Card";

interface StatsCardProps {
  title: string;
  value: string;
  change: string;
  changeType: "positive" | "negative" | "neutral";
  icon: ReactNode;
  iconBg?: string;
}

export function StatsCard({ title, value, change, changeType, icon, iconBg = "gradient-brand" }: StatsCardProps) {
  const changeColors = {
    positive: "text-green-600",
    negative: "text-red-600",
    neutral: "text-amber-600",
  };

  return (
    <Card>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-text-light text-sm">{title}</p>
          <p className="text-2xl font-bold text-text mt-1">{value}</p>
          <p className={`text-sm mt-2 ${changeColors[changeType]}`}>{change}</p>
        </div>
        <div className={`w-12 h-12 ${iconBg} rounded-xl flex items-center justify-center`}>
          {icon}
        </div>
      </div>
    </Card>
  );
}
