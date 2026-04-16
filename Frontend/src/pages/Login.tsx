import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, CloudRain, Thermometer, Wind, Droplets, Leaf, BarChart3 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/hooks/useAuth';

const floatingIcons = [
  { Icon: CloudRain, x: '15%', y: '20%', delay: 0, size: 32 },
  { Icon: Thermometer, x: '70%', y: '15%', delay: 0.5, size: 28 },
  { Icon: Wind, x: '80%', y: '60%', delay: 1, size: 34 },
  { Icon: Droplets, x: '25%', y: '70%', delay: 1.5, size: 26 },
  { Icon: Leaf, x: '55%', y: '40%', delay: 2, size: 30 },
  { Icon: BarChart3, x: '40%', y: '80%', delay: 0.8, size: 28 },
];

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login, register } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const resetForm = () => {
    setName(''); setEmail(''); setPassword(''); setConfirmPassword('');
    setError(''); setSuccess('');
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const success = await login(email, password);
    if (success) {
      navigate('/');
    } else {
      setError('Invalid email or password. Please try again.');
    }
    setIsLoading(false);
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    setIsLoading(true);
    const result = await register(name, email, password);
    setIsLoading(false);
    if (result.success) {
      setSuccess('Account created successfully! You can now sign in.');
      setTimeout(() => { resetForm(); setIsRegister(false); }, 1500);
    } else {
      setError(result.message || 'Registration failed. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left Panel — 60% with animated graphics */}
      <div className="hidden lg:flex w-[60%] relative overflow-hidden items-center justify-center">
        {/* Gradient background orbs */}
        <motion.div
          className="absolute w-[500px] h-[500px] rounded-full opacity-20 blur-[120px]"
          style={{ background: 'hsl(var(--primary))', top: '10%', left: '10%' }}
          animate={{ y: [0, -30, 0, 20, 0], x: [0, 15, -10, 5, 0], scale: [1, 1.1, 0.95, 1.05, 1] }}
          transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' as const }}
        />
        <motion.div
          className="absolute w-[400px] h-[400px] rounded-full opacity-15 blur-[100px]"
          style={{ background: 'hsl(var(--secondary))', bottom: '10%', right: '10%' }}
          animate={{ y: [0, 20, -15, 10, 0], scale: [1, 0.95, 1.1, 1, 1] }}
          transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' as const }}
        />
        <motion.div
          className="absolute w-[300px] h-[300px] rounded-full opacity-10 blur-[80px]"
          style={{ background: 'hsl(var(--accent))', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}
          animate={{ scale: [1, 1.15, 0.9, 1.05, 1] }}
          transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' as const }}
        />

        {/* Grid lines */}
        <div className="absolute inset-0 opacity-[0.03]" style={{
          backgroundImage: 'linear-gradient(hsl(var(--foreground)) 1px, transparent 1px), linear-gradient(90deg, hsl(var(--foreground)) 1px, transparent 1px)',
          backgroundSize: '60px 60px',
        }} />

        {/* Floating climate icons */}
        {floatingIcons.map(({ Icon, x, y, delay, size }, i) => (
          <motion.div
            key={i}
            className="absolute text-primary/30"
            style={{ left: x, top: y }}
            animate={{ y: [0, -20, 0, 15, 0], rotate: [0, 10, -5, 8, 0], opacity: [0.2, 0.5, 0.3, 0.6, 0.2] }}
            transition={{ duration: 6 + i, repeat: Infinity, delay, ease: 'easeInOut' as const }}
          >
            <Icon size={size} />
          </motion.div>
        ))}

        {/* Central branding */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          className="relative z-10 text-center px-12"
        >
          <motion.div
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 40, repeat: Infinity, ease: 'linear' }}
            className="w-24 h-24 mx-auto mb-8 rounded-full border border-primary/30 flex items-center justify-center"
          >
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center backdrop-blur-sm">
              <Leaf className="w-8 h-8 text-primary" />
            </div>
          </motion.div>

          <h1 className="text-5xl font-bold mb-4">
            <span className="text-gradient-primary">ClimaAI</span>
          </h1>
          <p className="text-muted-foreground text-lg max-w-md mx-auto leading-relaxed">
            AI-powered climate intelligence for India. Analyze trends, detect anomalies, and predict the future of our environment.
          </p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mt-10 flex gap-8 justify-center"
          >
            {[
              { label: 'Data Points', value: '2.4M+' },
              { label: 'States Covered', value: '28' },
              { label: 'Model Accuracy', value: '94.7%' },
            ].map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 + i * 0.15 }}
                className="text-center"
              >
                <div className="text-2xl font-bold text-foreground">{stat.value}</div>
                <div className="text-xs text-muted-foreground mt-1">{stat.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>
      </div>

      {/* Right Panel — 40% login form */}
      <div className="w-full lg:w-[40%] flex items-center justify-center p-6 sm:p-12 relative">
        <div className="absolute w-[300px] h-[300px] rounded-full blur-[120px] opacity-10" style={{ background: 'hsl(var(--primary))' }} />

        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-md relative z-10"
        >
          <div className="lg:hidden text-center mb-8">
            <h1 className="text-3xl font-bold text-gradient-primary">ClimaAI</h1>
            <p className="text-muted-foreground text-sm mt-1">Climate Intelligence Platform</p>
          </div>

          <div className="glass-strong p-8 sm:p-10 space-y-6">
            <div>
              <h2 className="text-2xl font-semibold text-foreground">
                {isRegister ? 'Create account' : 'Welcome back'}
              </h2>
              <p className="text-muted-foreground text-sm mt-1">
                {isRegister ? 'Sign up for a new account' : 'Sign in to your account'}
              </p>
            </div>

            <form onSubmit={isRegister ? handleRegister : handleLogin} className="space-y-4">
              {isRegister && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="space-y-2">
                  <Label htmlFor="name" className="text-muted-foreground">Full Name</Label>
                  <Input id="name" type="text" placeholder="Priya Sharma" value={name} onChange={(e) => setName(e.target.value)} required className="bg-muted/50 border-border/30 focus:border-primary/50 h-11" />
                </motion.div>
              )}

              <div className="space-y-2">
                <Label htmlFor="email" className="text-muted-foreground">Email</Label>
                <Input id="email" type="email" placeholder="you@climaai.in" value={email} onChange={(e) => setEmail(e.target.value)} required className="bg-muted/50 border-border/30 focus:border-primary/50 h-11" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-muted-foreground">Password</Label>
                <div className="relative">
                  <Input id="password" type={showPassword ? 'text' : 'password'} placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required className="bg-muted/50 border-border/30 focus:border-primary/50 h-11 pr-10" />
                  <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors">
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              {isRegister && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="space-y-2">
                  <Label htmlFor="confirmPassword" className="text-muted-foreground">Confirm Password</Label>
                  <div className="relative">
                    <Input id="confirmPassword" type={showConfirmPassword ? 'text' : 'password'} placeholder="••••••••" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required className="bg-muted/50 border-border/30 focus:border-primary/50 h-11 pr-10" />
                    <button type="button" onClick={() => setShowConfirmPassword(!showConfirmPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors">
                      {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </motion.div>
              )}

              {!isRegister && (
                <div className="flex items-center justify-between text-sm">
                  <label className="flex items-center gap-2 text-muted-foreground cursor-pointer">
                    <input type="checkbox" className="rounded border-border/50 bg-muted/50 text-primary focus:ring-primary/30 w-4 h-4" />
                    Remember me
                  </label>
                  <button type="button" className="text-primary hover:text-primary/80 transition-colors">Forgot password?</button>
                </div>
              )}

              {error && (
                <motion.p initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} className="text-destructive text-sm bg-destructive/10 p-3 rounded-lg border border-destructive/20">
                  {error}
                </motion.p>
              )}

              {success && (
                <motion.p initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} className="text-accent text-sm bg-accent/10 p-3 rounded-lg border border-accent/20">
                  {success}
                </motion.p>
              )}

              <Button type="submit" disabled={isLoading} className="w-full h-11 bg-primary text-primary-foreground hover:bg-primary/90 font-medium">
                {isLoading ? (
                  <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }} className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full" />
                ) : isRegister ? 'Create Account' : 'Sign In'}
              </Button>
            </form>

            <div className="text-center text-sm text-muted-foreground pt-2">
              <p>
                {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
                <button type="button" onClick={() => { resetForm(); setIsRegister(!isRegister); }} className="text-primary hover:text-primary/80 font-medium transition-colors">
                  {isRegister ? 'Sign In' : 'Register'}
                </button>
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Login;
