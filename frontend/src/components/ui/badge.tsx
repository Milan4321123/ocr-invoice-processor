import * as React from "react"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline"
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className = "", variant = "default", ...props }, ref) => {
    const baseClasses = "inline-flex items-center rounded-md px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
    
    const variantClasses = {
      default: "bg-blue-600 text-white shadow hover:bg-blue-700",
      secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200",
      destructive: "bg-red-600 text-white shadow hover:bg-red-700",
      outline: "text-gray-900 border border-gray-300 bg-white shadow-sm hover:bg-gray-50",
    }
    
    const classes = `${baseClasses} ${variantClasses[variant]} ${className}`
    
    return (
      <div
        ref={ref}
        className={classes}
        {...props}
      />
    )
  }
)
Badge.displayName = "Badge"

export { Badge }
