import { useEffect, useState } from "react";

// True only once `active` has stayed true for `delayMs`. Lets fast requests
// finish without flashing a "server is waking up" message at the user.
export default function useDelayedFlag(active, delayMs = 4000) {
  const [flag, setFlag] = useState(false);

  useEffect(() => {
    if (!active) {
      setFlag(false);
      return undefined;
    }
    const timer = setTimeout(() => setFlag(true), delayMs);
    return () => clearTimeout(timer);
  }, [active, delayMs]);

  return flag;
}
