export function randomIndex(length: number): number {
  if (!Number.isInteger(length) || length <= 0) {
    throw new RangeError('length debe ser un entero mayor que cero.')
  }

  const cryptoApi = globalThis.crypto

  if (cryptoApi?.getRandomValues) {
    const values = new Uint32Array(1)
    const limit = Math.floor(0x100000000 / length) * length

    do {
      cryptoApi.getRandomValues(values)
    } while (values[0] >= limit)

    return values[0] % length
  }

  return Math.floor(Math.random() * length)
}
