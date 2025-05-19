/**
 * Dropdown Select Component
 * 
 * A reusable dropdown selection component built on top of Taltech Styleguide's
 * Dropdown component. It provides a consistent interface for selecting options
 * from a list with customizable labels and values.
 * 
 * Features:
 * - Customizable label and options
 * - Controlled open/close state
 * - Primary variant styling
 * - Fixed positioning strategy
 * - Automatic option label display
 * 
 * @component
 */

import React from 'react';
import { 
  Dropdown, 
  TTNewDropdownToggle
} from 'taltech-styleguide';

/**
 * Props interface for the DropdownSelect component
 * 
 * @interface DropdownSelectProps
 * @property {string} id - Unique identifier for the dropdown
 * @property {string} label - Display label for the dropdown
 * @property {Array<{value: string, label: string}>} options - Array of selectable options
 * @property {string} selectedValue - Currently selected option value
 * @property {function} onSelect - Callback function when an option is selected
 * @property {boolean} isOpen - Current open/closed state of the dropdown
 * @property {function} setIsOpen - Function to update the open/closed state
 */
export interface DropdownSelectProps {
  id: string;
  label: string;
  options: { value: string; label: string }[];
  selectedValue: string;
  onSelect: (value: string) => void;
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

/**
 * DropdownSelect Component
 * 
 * Renders a dropdown selection interface with customizable options and labels.
 * The component uses Taltech Styleguide's Dropdown component with additional
 * features for controlled state management and consistent styling.
 * 
 * The dropdown displays either:
 * - The label of the selected option if one is selected
 * - A default "Select [label]" text if no option is selected
 * 
 * @param {DropdownSelectProps} props - Component props
 * @returns {JSX.Element} Rendered dropdown select component
 */
const DropdownSelect: React.FC<DropdownSelectProps> = ({
  id,
  label,
  options,
  selectedValue,
  onSelect,
  isOpen,
  setIsOpen
}) => (
  <div className="input-block">
    {/* Label for the dropdown */}
    <label htmlFor={id}>{label}</label>
    
    {/* Main dropdown component */}
    <Dropdown onToggle={() => setIsOpen(!isOpen)}>
      {/* Dropdown toggle button */}
      <TTNewDropdownToggle
        id={id}
        variant="primary"
      >
        {selectedValue 
          ? options.find(o => o.value === selectedValue)?.label 
          : `Select ${label.toLowerCase()}`
        }
      </TTNewDropdownToggle>
      
      {/* Dropdown menu with options */}
      <Dropdown.Menu
        popperConfig={{
          strategy: 'fixed'  // Use fixed positioning for consistent placement
        }}
        renderOnMount      // Render menu on mount for better performance
        show={isOpen}      // Control menu visibility
      >
        {/* Map through options to create menu items */}
        {options.map(option => (
          <Dropdown.Item
            key={option.value}
            onClick={() => {
              onSelect(option.value);
              setIsOpen(false);  // Close dropdown after selection
            }}
          >
            {option.label}
          </Dropdown.Item>
        ))}
      </Dropdown.Menu>
    </Dropdown>
  </div>
);

export default DropdownSelect; 