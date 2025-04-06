import React from 'react';
import { 
  Dropdown, 
  TTNewDropdownToggle
} from 'taltech-styleguide';

export interface DropdownSelectProps {
  id: string;
  label: string;
  options: { value: string; label: string }[];
  selectedValue: string;
  onSelect: (value: string) => void;
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

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
    <label htmlFor={id}>{label}</label>
    <Dropdown onToggle={() => setIsOpen(!isOpen)}>
      <TTNewDropdownToggle
        id={id}
        variant="primary"
      >
        {selectedValue ? options.find(o => o.value === selectedValue)?.label : `Select ${label.toLowerCase()}`}
      </TTNewDropdownToggle>
      <Dropdown.Menu
        popperConfig={{
          strategy: 'fixed'
        }}
        renderOnMount
        show={isOpen}
      >
        {options.map(option => (
          <Dropdown.Item
            key={option.value}
            onClick={() => {
              onSelect(option.value);
              setIsOpen(false);
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