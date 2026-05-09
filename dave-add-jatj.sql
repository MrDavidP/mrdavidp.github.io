-- Add Joe & The Juice to the front of Dave's tips array
update public.contributors
set tips = (
  '[{"url":"tip-jatj.html","photo":"joe-and-the-juice-geneva.jpg","category":"Café · Juice","place":"Joe & The Juice","hood":"Place de Hollande","city":"Geneva","copy":"Geneva just got one. The queue on day one says everything about what this city has been missing."}]'::jsonb
  ||
  tips::jsonb
)::text
where handle = 'dave';
