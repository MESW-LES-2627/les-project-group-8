<script lang="ts">
  import "../app.css";
  import { enhance } from "$app/forms";
  import type { PageProps } from "./$types";
  import type { PoolStatus } from "./+page.server";

  let { data, form }: PageProps = $props();

  let submitting = $state(false);

  // Avoids SSR hydration mismatch: render UTC on the server, local time after mounting.
  let hydrated = $state(false);
  $effect(() => {
    hydrated = true;
  });

  // ID of the pool created in the latest form action, used to highlight it in the list.
  let createdId = $derived(form && "created" in form ? form.created : null);
  let values = $derived(form && "values" in form ? form.values : undefined);
  let error = $derived(form && "error" in form ? form.error : undefined);

  const statusStyles: Record<PoolStatus, string> = {
    OPEN: "bg-emerald-50 text-emerald-700 border-emerald-200",
    LOCKED: "bg-amber-50 text-amber-700 border-amber-200",
    RESOLVED: "bg-sky-50 text-sky-700 border-sky-200",
  };

  function formatDeadline(deadline: string, localTime: boolean): string {
    return (
      new Intl.DateTimeFormat("en-GB", {
        dateStyle: "medium",
        timeStyle: "short",
        timeZone: localTime ? undefined : "UTC",
      }).format(new Date(deadline)) + (localTime ? "" : " UTC")
    );
  }
</script>

<svelte:head>
  <title>Friendly Pools: call it before it happens</title>
  <meta
    name="description"
    content="Create zero-money prediction pools with your friends and settle who was right."
  />
</svelte:head>

<main class="mx-auto max-w-6xl px-6 py-12 lg:py-16">
  <header class="max-w-2xl">
    <p
      class="inline-flex items-center gap-2 rounded-full border border-orange-200 bg-orange-50 px-3 py-1 text-xs font-medium text-orange-700"
    >
      <span class="size-1.5 rounded-full bg-[#ff3e00]"></span>
      Iteration 0 · thin vertical slice
    </p>
    <h1
      class="mt-4 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl"
    >
      Call it <span class="text-[#ff3e00]">before it happens</span>.
    </h1>
    <p class="mt-3 text-lg text-slate-600">
      Create a pool, pick a side, and settle once and for all who saw it coming.
      Bragging rights only.
    </p>
  </header>

  <div class="mt-10 grid gap-8 lg:grid-cols-[minmax(0,26rem)_1fr]">
    <section
      aria-labelledby="create-heading"
      class="h-fit rounded-xl border border-slate-200 bg-white p-6 shadow-xs lg:sticky lg:top-8"
    >
      <h2 id="create-heading" class="text-xl font-semibold text-slate-900">
        New pool
      </h2>

      <form
        id="create-pool-form"
        method="POST"
        action="?/create"
        class="mt-6 space-y-4"
        use:enhance={({ formData }) => {
          // <input type="datetime-local"> lacks timezone info; send browser offset so server can resolve UTC.
          formData.set("tzOffset", String(new Date().getTimezoneOffset()));
          submitting = true;
          return async ({ update }) => {
            await update();
            submitting = false;
          };
        }}
      >
        <div>
          <label
            class="mb-1.5 block text-sm font-medium text-slate-700"
            for="pool-name">Title</label
          >
          <input
            id="pool-name"
            name="name"
            class="block w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-slate-900 placeholder:text-slate-400 focus:border-[#ff3e00] focus:ring-2 focus:ring-[#ff3e00]/20"
            required
            maxlength="120"
            placeholder="Champions League Final"
            value={values?.name ?? ""}
          />
        </div>

        <div>
          <label
            class="mb-1.5 block text-sm font-medium text-slate-700"
            for="pool-statement">Statement</label
          >
          <textarea
            id="pool-statement"
            name="statement"
            class="block w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-slate-900 placeholder:text-slate-400 focus:border-[#ff3e00] focus:ring-2 focus:ring-[#ff3e00]/20 min-h-24 resize-y"
            required
            maxlength="500"
            placeholder="Real Madrid wins in 90 minutes."
            value={values?.statement ?? ""}></textarea>
        </div>

        <fieldset>
          <legend class="mb-1.5 block text-sm font-medium text-slate-700"
            >Outcomes</legend
          >
          <div class="grid grid-cols-2 gap-3">
            <input
              id="pool-option-a"
              name="optionA"
              class="block w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-slate-900 placeholder:text-slate-400 focus:border-[#ff3e00] focus:ring-2 focus:ring-[#ff3e00]/20"
              required
              maxlength="100"
              placeholder="Yes"
              aria-label="First outcome"
              value={values?.optionA ?? ""}
            />
            <input
              id="pool-option-b"
              name="optionB"
              class="block w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-slate-900 placeholder:text-slate-400 focus:border-[#ff3e00] focus:ring-2 focus:ring-[#ff3e00]/20"
              required
              maxlength="100"
              placeholder="No"
              aria-label="Second outcome"
              value={values?.optionB ?? ""}
            />
          </div>
        </fieldset>

        <div>
          <label
            class="mb-1.5 block text-sm font-medium text-slate-700"
            for="pool-deadline">Locks at</label
          >
          <input
            id="pool-deadline"
            name="deadline"
            type="datetime-local"
            class="block w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-slate-900 placeholder:text-slate-400 focus:border-[#ff3e00] focus:ring-2 focus:ring-[#ff3e00]/20"
            required
            value={values?.deadline ?? ""}
          />
        </div>

        <!-- Overwritten by enhance with the browser's offset; 0 (UTC) without JS. -->
        <input type="hidden" name="tzOffset" value="0" />

        {#if error}
          <p
            id="create-pool-error"
            role="alert"
            class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800"
          >
            {error}
          </p>
        {/if}

        <button
          id="create-pool-submit"
          type="submit"
          disabled={submitting}
          class="w-full rounded-lg bg-[#ff3e00] px-5 py-2.5 font-semibold text-white shadow-xs transition hover:bg-[#ea3600] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#ff3e00] disabled:cursor-wait disabled:opacity-60"
        >
          {submitting ? "Creating…" : "Create pool"}
        </button>
      </form>
    </section>
  </div>
</main>
