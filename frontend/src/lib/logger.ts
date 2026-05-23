type LogLevel = 'debug' | 'info' | 'warn' | 'error'

function write(level: LogLevel, message: string, ...args: unknown[]) {
  const prefix = `[Cyberify KB] ${message}`
  if (level === 'error') {
    console.error(prefix, ...args)
    return
  }
  if (level === 'warn') {
    console.warn(prefix, ...args)
    return
  }
  if (level === 'info') {
    console.info(prefix, ...args)
    return
  }
  console.debug(prefix, ...args)
}

export const logger = {
  debug: (message: string, ...args: unknown[]) => write('debug', message, ...args),
  info: (message: string, ...args: unknown[]) => write('info', message, ...args),
  warn: (message: string, ...args: unknown[]) => write('warn', message, ...args),
  error: (message: string, ...args: unknown[]) => write('error', message, ...args),
}
