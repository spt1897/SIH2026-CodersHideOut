import { useState } from 'react';

export default function SignupForm() {
  const [role, setRole] = useState('PUBLIC');

  return (
    <form className="flex flex-col gap-4 max-w-md mx-auto p-6 bg-white dark:bg-slate-50 shadow-md rounded-lg">
      <h2 className="text-xl font-bold text-blue-950">System Registration</h2>
      
      <label className="text-sm font-medium text-gray-700">Account Type</label>
      <select 
        value={role} 
        onChange={(e) => setRole(e.target.value)}
        className="p-2 border rounded border-gray-300"
      >
        <option value="PUBLIC">Public / Citizen</option>
        <option value="OFFICIAL">Government Official / Responder</option>
      </select>

      {/* Public Fields */}
      <input type="tel" placeholder="Mobile Number (Required)" className="p-2 border rounded" required />
      <input type="text" placeholder="Full Name (Optional)" className="p-2 border rounded" />
      <input type="text" placeholder="Home Location / Pin Code" className="p-2 border rounded" />

      {/* Official Fields - Only show if OFFICIAL is selected */}
      {role === 'OFFICIAL' && (
        <div className="flex flex-col gap-4 mt-2 p-4 bg-gray-100 rounded border border-gray-200">
          <h3 className="text-sm font-bold text-blue-950">Official Identity Verification</h3>
          
          {/* Email must enforce domains like @gov.in or @nic.in */}
          <input type="email" placeholder="Official Email (@gov.in / @nic.in)" className="p-2 border rounded" required />
          <input type="text" placeholder="Full Name & Designation" className="p-2 border rounded" required />
          
          {/* Department Selection Dropdown */}
          <select className="p-2 border rounded border-gray-300" required>
            <option value="">Select Department...</option>
            <option value="NDMA">NDMA (National Level)</option>
            <option value="SDMA">SDMA (State Level)</option>
            <option value="DDMA">DDMA (District Level)</option>
            <option value="NDRF">NDRF / SDRF</option>
            <option value="POLICE">Police & Fire Services</option>
            <option value="NHAI">NHAI / BRO (Infrastructure)</option>
            <option value="GSI">GSI (Field Geologist)</option>
          </select>

          {/* Spatial Jurisdiction */}
          <div className="grid grid-cols-2 gap-2">
            <input type="text" placeholder="State Code" className="p-2 border rounded" required />
            <input type="text" placeholder="District Code" className="p-2 border rounded" required />
          </div>

          <label className="text-xs text-gray-500 font-medium">Upload Government/Agency ID Proof</label>
          <input type="file" className="text-xs" required />
        </div>
      )}

      <button type="submit" className="bg-blue-900 text-white p-2 rounded hover:bg-blue-950 mt-2">
        Register Account
      </button>
    </form>
  );
}