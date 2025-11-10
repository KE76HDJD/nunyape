import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Presentation, 
  Users, 
  Settings, 
  HelpCircle,
  CreditCard
} from 'lucide-react';

const Sidebar = () => {
  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Présentations', href: '/presentations', icon: Presentation },
    { name: 'Questions', href: '/questions', icon: HelpCircle },
    { name: 'Paiements', href: '/payments', icon: CreditCard },
    { name: 'Utilisateurs', href: '/users', icon: Users },
    { name: 'Paramètres', href: '/settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white shadow-sm border-r border-gray-200">
      <nav className="p-4">
        <div className="space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`
                }
              >
                <Icon className="h-5 w-5" />
                <span className="font-medium">{item.name}</span>
              </NavLink>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="mt-8">
          <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Actions rapides
          </h3>
          <div className="mt-2 space-y-2">
            <NavLink
              to="/presentation/create"
              className="flex items-center space-x-3 px-3 py-2 rounded-lg bg-primary-600 text-white hover:bg-primary-700 transition-colors"
            >
              <Presentation className="h-5 w-5" />
              <span className="font-medium">Nouvelle présentation</span>
            </NavLink>
          </div>
        </div>
      </nav>
    </aside>
  );
};

export default Sidebar;