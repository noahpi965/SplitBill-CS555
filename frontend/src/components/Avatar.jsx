// Shows a user's uploaded avatar (US15) or falls back to their initial.
export default function Avatar({ name, src, large }) {
  if (src) return <img className={`avatar-img${large ? ' avatar-lg' : ''}`} src={src} alt={name} />
  return <span className={`avatar${large ? ' avatar-lg' : ''}`}>{(name || '?').charAt(0).toUpperCase()}</span>
}
