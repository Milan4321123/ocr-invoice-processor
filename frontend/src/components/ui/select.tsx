import * as React from "react"

interface SelectContextType {
  value?: string
  onValueChange?: (value: string) => void
  open?: boolean
  onOpenChange?: (open: boolean) => void
}

const SelectContext = React.createContext<SelectContextType>({})

const Select = ({ 
  children, 
  value, 
  onValueChange,
  open,
  onOpenChange 
}: {
  children: React.ReactNode
  value?: string
  onValueChange?: (value: string) => void
  open?: boolean
  onOpenChange?: (open: boolean) => void
}) => {
  const [internalOpen, setInternalOpen] = React.useState(false)
  const isOpen = open !== undefined ? open : internalOpen
  const setIsOpen = onOpenChange || setInternalOpen

  return (
    <SelectContext.Provider value={{
      value,
      onValueChange,
      open: isOpen,
      onOpenChange: setIsOpen
    }}>
      <div className="relative">
        {children}
      </div>
    </SelectContext.Provider>
  )
}

const SelectTrigger = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ className = "", children, ...props }, ref) => {
  const context = React.useContext(SelectContext)
  
  return (
    <button
      ref={ref}
      className={`flex h-9 w-full items-center justify-between whitespace-nowrap rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm ring-offset-background placeholder:text-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      onClick={() => context.onOpenChange?.(!context.open)}
      {...props}
    >
      {children}
      <svg
        className="h-4 w-4 opacity-50"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="m6 9 6 6 6-6" />
      </svg>
    </button>
  )
})
SelectTrigger.displayName = "SelectTrigger"

const SelectValue = ({ placeholder }: { placeholder?: string }) => {
  const context = React.useContext(SelectContext)
  return <span>{context.value || placeholder}</span>
}

const SelectContent = ({ 
  children, 
  className = "" 
}: { 
  children: React.ReactNode
  className?: string 
}) => {
  const context = React.useContext(SelectContext)
  
  if (!context.open) return null
  
  return (
    <div className={`absolute top-full left-0 z-50 min-w-[8rem] overflow-hidden rounded-md border bg-white shadow-lg ${className}`}>
      <div className="p-1">
        {children}
      </div>
    </div>
  )
}

const SelectItem = ({ 
  children, 
  value, 
  className = "" 
}: { 
  children: React.ReactNode
  value: string
  className?: string 
}) => {
  const context = React.useContext(SelectContext)
  
  return (
    <div
      className={`relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-2 pr-8 text-sm outline-none hover:bg-gray-100 focus:bg-gray-100 ${className}`}
      onClick={() => {
        context.onValueChange?.(value)
        context.onOpenChange?.(false)
      }}
    >
      {children}
    </div>
  )
}

export { Select, SelectTrigger, SelectValue, SelectContent, SelectItem }
