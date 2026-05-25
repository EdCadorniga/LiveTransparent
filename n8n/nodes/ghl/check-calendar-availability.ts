interface CalendarSlot {
  date: string
  day: string
  slots: { time: string; epochMs: number }[]
}

interface FreeSlotsResponse {
  [date: string]: { slots: string[] } | string
}

type CheckResult =
  | { success: true; slots: CalendarSlot[]; totalSlots: number }
  | { success: false; error: string }

async function checkCalendarAvailability(params: {
  calendarId?: string
  startDate?: number
  endDate?: number
  timezone?: string
  maxSlots?: number
}): Promise<CheckResult> {
  const calendarId = params.calendarId || 'SrtXcFVyea7pFl3nTiIK'
  const now = Date.now()
  const startDate = params.startDate || now
  const endDate = params.endDate || now + 7 * 24 * 60 * 60 * 1000
  const timezone = params.timezone || 'America/New_York'
  const maxSlots = params.maxSlots || 10

  const token = $env.GHL_PIT

  if (!token) {
    return { success: false, error: 'GHL_PIT env variable not set' }
  }

  try {
    const qs = new URLSearchParams({
      startDate: String(startDate),
      endDate: String(endDate),
      timezone,
    })

    const response = await fetch(
      `https://services.leadconnectorhq.com/calendars/${calendarId}/free-slots?${qs}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      const text = await response.text()
      return { success: false, error: `GHL API ${response.status}: ${text}` }
    }

    const raw: FreeSlotsResponse = await response.json()
    const traceId = typeof raw.traceId === 'string' ? raw.traceId : undefined

    const calendarSlots: CalendarSlot[] = []

    for (const [dateStr, value] of Object.entries(raw)) {
      if (dateStr === 'traceId') continue
      if (!value || typeof value !== 'object' || !Array.isArray((value as any).slots)) continue

      const slots = (value as { slots: string[] }).slots
      const day = new Date(dateStr).toLocaleDateString('en-US', {
        weekday: 'short',
        timeZone: timezone,
      })

      calendarSlots.push({
        date: dateStr,
        day,
        slots: slots.map((iso) => ({
          time: new Date(iso).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            timeZone,
          }),
          epochMs: new Date(iso).getTime(),
        })),
      })
    }

    const allSlots = calendarSlots.flatMap((d) => d.slots)

    return {
      success: true,
      slots: calendarSlots,
      totalSlots: allSlots.length,
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    return { success: false, error: message }
  }
}
